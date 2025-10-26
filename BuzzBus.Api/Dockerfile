# Use the official .NET 8 runtime as base image
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 5000

# Use the official .NET 8 SDK for building
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["BuzzBus.Api.csproj", "./"]
RUN dotnet restore "BuzzBus.Api.csproj"
COPY . .
RUN dotnet build "BuzzBus.Api.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "BuzzBus.Api.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "BuzzBus.Api.dll"]
