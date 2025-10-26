using BuzzBus.Api.Services;
using BuzzBus.Api.Controllers;
using BuzzBus.Api.Models;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactApp", policy =>
    {
        policy.WithOrigins(
                "http://localhost:3000",
                "https://buzzbus.netlify.app",
                "https://buzzbus.vercel.app",
                "https://*.netlify.app",
                "https://*.vercel.app"
              )
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

// Add HttpClient
builder.Services.AddHttpClient<ITranslocApiService, TranslocApiService>();

// Add custom services
builder.Services.AddScoped<IRouteService, RouteService>();

// Add configuration
builder.Services.Configure<TranslocApiSettings>(
    builder.Configuration.GetSection("TranslocApi"));

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Configure port for production
var port = Environment.GetEnvironmentVariable("PORT") ?? "5000";
var url = $"http://0.0.0.0:{port}";

app.UseHttpsRedirection();

app.UseCors("AllowReactApp");

app.UseAuthorization();

app.MapControllers();

app.Run(url);
