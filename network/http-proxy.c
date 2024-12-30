//
// Created by Kingson Wu on 2023/6/7.
//
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define BUFFER_SIZE 4096

void error(const char *msg) {
    perror(msg);
    exit(1);
}

void proxy(int client_sock, const char *server_ip, int server_port) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_received, bytes_sent;

    // 创建与服务器的连接
    int server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock < 0) {
        error("Error creating server socket");
    }

    // 设置服务器地址
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(server_ip);
    server_addr.sin_port = htons(server_port);

    // 连接到服务器
    if (connect(server_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        error("Error connecting to server");
    }

    while (1) {
        // 从客户端接收数据
        bytes_received = recv(client_sock, buffer, BUFFER_SIZE, 0);
        if (bytes_received <= 0) {
            break;
        }

        // 将数据发送到服务器
        bytes_sent = send(server_sock, buffer, bytes_received, 0);
        if (bytes_sent < 0) {
            error("Error sending data to server");
        }

        // 从服务器接收数据
        bytes_received = recv(server_sock, buffer, BUFFER_SIZE, 0);
        if (bytes_received <= 0) {
            break;
        }

        // 将数据发送回客户端
        bytes_sent = send(client_sock, buffer, bytes_received, 0);
        if (bytes_sent < 0) {
            error("Error sending data to client");
        }
    }

    close(client_sock);
    close(server_sock);
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <proxy_port> <server_ip> <server_port>\n", argv[0]);
        exit(1);
    }

    int proxy_port = atoi(argv[1]);
    char *server_ip = argv[2];
    int server_port = atoi(argv[3]);

    // 创建代理服务器套接字
    int proxy_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (proxy_sock < 0) {
        error("Error creating proxy socket");
    }

    // 设置代理服务器地址
    struct sockaddr_in proxy_addr;
    memset(&proxy_addr, 0, sizeof(proxy_addr));
    proxy_addr.sin_family = AF_INET;
    proxy_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    proxy_addr.sin_port = htons(proxy_port);

    // 将代理服务器绑定到指定端口
    if (bind(proxy_sock, (struct sockaddr *)&proxy_addr, sizeof(proxy_addr)) < 0) {
        error("Error binding proxy socket");
    }

    // 监听传入的连接
    if (listen(proxy_sock, 5) < 0) {
        error("Error listening for connections");
    }

    printf("Proxy server running on port %d\n", proxy_port);

    while (1) {
        // 接受客户端连接
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_sock = accept(proxy_sock, (struct sockaddr *)&client_addr, &client_len);
        if (client_sock < 0) {
            error("Error accepting client connection");
        }

        printf("Client connected: %s:%d\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        // 创建子进程处理代理请求
        pid_t pid = fork();
        if (pid < 0) {
            error("Error creating child process");
        } else if (pid == 0) {
            // 子进程处理代理请求
            close(proxy_sock);
            proxy(client_sock, server_ip, server_port);
            exit(0);
        } else {
            // 父进程继续监听传入的连接
            close(client_sock);
        }
    }

    close(proxy_sock);

    return 0;
}