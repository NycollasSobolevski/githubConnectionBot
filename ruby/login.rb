require "json"
require "net/http"
require "uri"

require "./requests.rb"

def login
  verification_uri, user_code, device_code, interval = request_device_code.values_at("verification_uri", "user_code", "device_code", "interval")

  puts "Please visit: #{verification_uri}"
  puts "and enter code: #{user_code}"

  poll_for_token(device_code, interval)

  puts "Successfully authenticated!"
end
