#!/usr/bin/env ruby

require "fileutils"
require "./help.rb"
require "./login.rb"
require "./whoami.rb"
require "./Projects.rb"


def main
  case ARGV[0]
  when "help"
    help

  when "login"
    login

  when "whoami"
    whoami

  when "project"
    get_project_items(9)

  else
    puts "Unknown command `#{ARGV[0]}`"
  end
end

main
