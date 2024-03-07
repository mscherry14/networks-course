package main

import (
	"bufio"
	"fmt"
	"net"
	"net/http"
	"net/http/httputil"
	"os"
	"strings"
)

func main() {
	listener, _ := net.Listen("tcp", ":"+os.Args[1]) // открываем слушающий сокет
	fmt.Println("server started")
	for {
		conn, err := listener.Accept() // принимаем TCP-соединение от клиента и создаем новый сокет
		if err != nil {
			continue
		}
		go handleClient(conn) // обрабатываем запросы клиента в отдельной го-рутине
	}
}

func handleClient(conn net.Conn) {
	defer conn.Close() // закрываем сокет при выходе из функции

	scanner := bufio.NewScanner(conn)
	for scanner.Scan() {
		ln := scanner.Bytes()
		if strings.Fields(string(ln))[0] == "GET" {
			file, err := os.Open("./" + strings.Fields(string(ln))[1]) // For read access.
			if err != nil {
				resp := http.Response{
					Status:        "404 Not Found",
					StatusCode:    404,
					Proto:         "HTTP/1.1",
					ProtoMajor:    1,
					ProtoMinor:    1,
					ContentLength: 0,
					Header:        make(http.Header, 0),
				}
				byteResp, _ := httputil.DumpResponse(&resp, true)
				fmt.Println(string(byteResp))
				conn.Write(byteResp)
				return
			}
			fi, err := file.Stat()
			if err != nil {
				resp := http.Response{
					Status:        "404 Not Found",
					StatusCode:    404,
					Proto:         "HTTP/1.1",
					ProtoMajor:    1,
					ProtoMinor:    1,
					ContentLength: 0,
					Header:        make(http.Header, 0),
				}
				byteResp, _ := httputil.DumpResponse(&resp, true)
				fmt.Println(string(byteResp))
				conn.Write(byteResp)
				return
			}
			resp := http.Response{
				Status:        "200 OK",
				StatusCode:    200,
				Proto:         "HTTP/1.1",
				ProtoMajor:    1,
				ProtoMinor:    1,
				ContentLength: fi.Size(),
				Body:          file,
			}
			byteResp, _ := httputil.DumpResponse(&resp, true)
			fmt.Println(string(byteResp))
			conn.Write(byteResp)
			return
		}
	}
}
