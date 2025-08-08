package com.allnight.potendayBE;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class PotendayBeApplication {

	public static void main(String[] args) {
		SpringApplication.run(PotendayBeApplication.class, args);
	}

}
