using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace HelloWorld;

public static class Program
{
    private const string API = "http://localhost:31415";

    public static async Task Main(string[] args)
    {
        try
        {
            using var client = new HttpClient();
            
            var toastRequest = new ShowToastRequest
            {
                Text = "Hello from your first C# plugin!",
                IconType = 2,
                Priority = 5,
                DurationSeconds = 5
            };
            
            await client.PostAsJsonAsync($"{API}/showtoast", toastRequest, HelloWorldJsonContext.Default.ShowToastRequest);
            
            Console.WriteLine("Plugin executed successfully!");
        }
        catch (Exception error)
        {
            Console.WriteLine($"Error: {error.Message}");
        }
    }
}

public record ShowToastRequest
{
    [JsonPropertyName("text")]
    public string Text { get; init; } = "";
    
    [JsonPropertyName("iconType")]
    public int IconType { get; init; }
    
    [JsonPropertyName("priority")]
    public int Priority { get; init; }
    
    [JsonPropertyName("durationSeconds")]
    public int DurationSeconds { get; init; }
}

[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
[JsonSerializable(typeof(ShowToastRequest))]
internal sealed partial class HelloWorldJsonContext : JsonSerializerContext
{
}
