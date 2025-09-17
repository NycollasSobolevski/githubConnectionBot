require "json"
require "net/http"
require "uri"
require "./_secrets.rb"

def parse_response(response)
  case response
  when Net::HTTPOK, Net::HTTPCreated
    JSON.parse(response.body)
  when Net::HTTPUnauthorized
    puts "You are not authorized. Run the `login` command"
    exit 1
  else
    puts response
    puts response.body
    exit 1
  end
end

def request_device_code
  uri = URI("https://github.com/login/device/code")
  parameters = URI.encode_www_form("client_id" => CLIENT_ID)
  headers = {"Accept" => "application/json"}

  response = Net::HTTP.post(uri, parameters, headers)
  parse_response(response)
end

def request_token(device_code)
  uri = URI("https://github.com/login/oauth/access_token")
  parameters = URI.encode_www_form({
    "client_id" => CLIENT_ID,
    "device_code" => device_code,
    "grant_type" => "urn:ietf:params:oauth:grant-type:device_code"
  })
  headers = {"Accept" => "application/json"}
  response = Net::HTTP.post(uri, parameters, headers)
  puts response.body
  parse_response(response)
end

def poll_for_token(device_code, interval)

  loop do
    response = request_token(device_code)
    error, access_token = response.values_at("error", "access_token")

    if error
      case error
      when "authorization_pending"
        # The user has not yet entered the code.
        # Wait, then poll again.
        sleep interval
        next
      when "slow_down"
        # The app polled too fast.
        # Wait for the interval plus 5 seconds, then poll again.
        sleep interval + 5
        next
      when "expired_token"
        # The `device_code` expired, and the process needs to restart.
        puts "The device code has expired. Please run `login` again."
        exit 1
      when "access_denied"
        # The user cancelled the process. Stop polling.
        puts "Login cancelled by user."
        exit 1
      else
        puts response
        exit 1
      end
    end

    File.write("./.token", access_token)

    # Set the file permissions so that only the file owner can read or modify the file
    FileUtils.chmod(0600, "./.token")

    break
  end
end

def login
  verification_uri, user_code, device_code, interval = request_device_code.values_at("verification_uri", "user_code", "device_code", "interval")

  puts "Please visit: #{verification_uri}"
  puts "and enter code: #{user_code}"

  poll_for_token(device_code, interval)

  puts "Successfully authenticated!"
end