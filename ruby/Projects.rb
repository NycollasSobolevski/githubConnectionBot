def get_project_items(project_number)
  uri = URI("https://api.github.com/orgs/Engineering-Technical-School-Bosch-CWB/projectsV2/#{project_number}/items")

  begin
    token = File.read("./.token").strip
  rescue Errno::ENOENT => e
    puts "You are not authorized. run the `login` command."
    exit 1
  end

  response = Net::HTTP.start(uri.host, uri.port, use_ssl: true) do |http|
    body = {"access_token": token}.to_json
    headers = {
      "Accept" => "application/vnd.github+json",
      "Authorization" => "Bearer #{token}"
    }

    http.send_request("GET", uri.path, body, headers)
  end

  parsed_response = parse_response(response)
  puts "You are #{parsed_response}"

end