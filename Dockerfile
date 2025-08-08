# 1단계: Build with Gradle
FROM gradle:8.4-jdk17 AS build
WORKDIR /app

# 필요한 파일 복사
COPY . .

# JAR 빌드
RUN gradle bootJar --no-daemon

# 2단계: Run with JRE
FROM eclipse-temurin:17-jre
WORKDIR /app

# 빌드 결과 복사
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-Dspring.profiles.active=dev", "-jar", "app.jar"]
