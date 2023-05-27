#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 1666

void handle_request(int client_socket) {
    char buffer[1024];
    ssize_t bytes_read;

    // 读取请求头和URI
    while ((bytes_read = read(client_socket, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[bytes_read] = '\0';

        // 打印请求头
        printf("%s", buffer);

        // 检查是否到达请求头的结尾
        if (strstr(buffer, "\r\n\r\n")) {
            break;
        }
    }

    // 解析请求的URI
    char *uri = strtok(buffer, " ");
    if (uri != NULL) {
        uri = strtok(NULL, " ");
        if (uri != NULL) {
            printf("Request URI: %s\n", uri);
        }
    }

    // 生成HTTP响应
    const char *response = "HTTP/1.1 200 OK\r\n"
                           "Content-Type: text/plain\r\n"
                           "\r\n"
                           "Hello, World!\r\n";
    write(client_socket, response, strlen(response));

    // 关闭客户端连接
    close(client_socket);
}

int main() {
    int server_socket, client_socket;
    struct sockaddr_in server_address, client_address;
    socklen_t client_address_length;

    // 创建套接字
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == -1) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // 设置服务器地址
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(PORT);
    server_address.sin_addr.s_addr = INADDR_ANY;

    // 绑定套接字到地址和端口
    if (bind(server_socket, (struct sockaddr *) &server_address, sizeof(server_address)) == -1) {
        perror("bind");
        exit(EXIT_FAILURE);
    }

    // 监听连接
    if (listen(server_socket, 10) == -1) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d\n", PORT);

    // 接受并处理客户端连接
    while (1) {
        client_address_length = sizeof(client_address);
        client_socket = accept(server_socket, (struct sockaddr *) &client_address, &client_address_length);
        if (client_socket == -1) {
            perror("accept");
            continue;
        }

        // 打印客户端信息
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &(client_address.sin_addr), client_ip, INET_ADDRSTRLEN);
        printf("Connection accepted from %s:%d\n", client_ip, ntohs(client_address.sin_port));

        // 处理客户端请求
        handle_request(client_socket);
    }

    // 关闭服务器套接字
    close(server_socket);

    return 0;
}
