package main

import (
	"os"
	"io"
	"fmt"
	"log"
	"net"
	"bytes"
	"strings"
	"strconv"
	"net/http"
	"encoding/json"

	"github.com/joho/godotenv"
)

const CF_URL = "https://api.cloudflare.com/client/v4/zones/"

type DNSConfig struct {
	Key string
	Zone string
	Proxy bool
	Dns []string

	Device string
	Ip string
	Type string
}

type DNSRecord struct {
	Id string `json:"id"`
	Name string `json:"name"`
	Type string `json:"type"`
	Content string `json:"content"`

	Success bool `json:"success"`
}

type DNSResult struct {
	Result []DNSRecord `json:"result"`
}


func create_config() DNSConfig {
	if len(os.Args) < 2 {
		log.Fatal("Missing configuration file")
	}

	if err := godotenv.Load(os.Args[1]); err != nil {
		log.Fatal(err)
	}

	proxy, err := strconv.ParseBool(os.Getenv("CF_PROXY"))

	if err != nil {
		log.Fatal(err)
	}


	cf_config := DNSConfig{
		Device: os.Getenv("NETWORK_DEVICE"),
		Key: os.Getenv("CF_KEY"),
		Zone: os.Getenv("CF_ZONE"),
		Proxy: proxy,

		Dns: strings.Split(os.Getenv("CF_DNS"), ","),
	}

	net_dev, err := net.InterfaceByName(cf_config.Device)

	if err != nil {
		log.Fatal(err)
	}

	net_addrs, err := net_dev.Addrs()

	for _, a := range net_addrs {
		ipNet, ok := a.(*net.IPNet)

		if ok || ipNet.IP.IsGlobalUnicast() {
			if ipNet.IP.To4() == nil {
				cf_config.Ip = ipNet.IP.String()
				cf_config.Type = "AAAA"

				break
			}
		}
	}

	return cf_config
}

func get_records(config DNSConfig) []DNSRecord {
	var dns_data DNSResult

	client := &http.Client{}
	req, err := http.NewRequest("GET", fmt.Sprintf("%s/%s/%s", CF_URL, config.Zone, "dns_records"), nil)

	if err != nil {
		log.Fatal(err)

	}

	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", config.Key))

	resp, err := client.Do(req)

	if err != nil {
		log.Fatal(err)

	}

	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)

	if err != nil {
		log.Fatal(err)

	}

	err = json.Unmarshal(body, &dns_data)

	if err != nil {
		log.Fatal(err)
	}

	return dns_data.Result
}

func patch_record(config DNSConfig, record DNSRecord) {
	// Update ip to device ip
	record.Content = config.Ip

	request_data, _ := json.Marshal(record)
	request_url := fmt.Sprintf("%s/%s/%s/%s", CF_URL, config.Zone, "dns_records", record.Id)

	client := &http.Client{}
	req, err := http.NewRequest("PATCH", request_url, bytes.NewBuffer(request_data))

	if err != nil {
		log.Fatal(err)
	}

	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", config.Key))

	resp, err := client.Do(req)

	if err != nil {
		log.Fatal(err)

	}

	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)

	if err != nil {
		log.Fatal(err)

	}

	var dns_data DNSRecord

	err = json.Unmarshal(body, &dns_data)

	if err != nil {
		log.Fatal(err)
	}

	if dns_data.Success {
		log.Printf("Updated %s\n", record.Name)
	} else {
		log.Printf("Failed to update %s\n", record.Name)
	}
}

func main() {

	cf_config := create_config()
	cf_records := get_records(cf_config)

	log.Printf("Device IP: %s\n", cf_config.Ip)

	for _, cf_record := range cf_records {

		for _, target_dns := range cf_config.Dns {
			if cf_record.Name == target_dns && cf_config.Ip != cf_record.Content {
				log.Printf("Record: %s, IP %s, New IP %s", cf_record.Name, cf_record.Content, cf_config.Ip)
				patch_record(cf_config, cf_record)
				break
			} else if cf_record.Name == target_dns && cf_config.Ip == cf_record.Content {
				log.Printf("Record: %s already updated, ignoring", target_dns)
				break
			}
		}
	}
}
