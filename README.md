# Dockless

## Overview

Dockless (Docker + Serverless) is an experimental project aimed at locally implementing a simple system that manages serverless functions, inspired by how AWS Lambda works, all while utilizing Docker.

## Key Features:
* Multi-language support → Initially compatible with Python and TypeScript, allowing the execution of functions in different runtimes as needed.
* On-demand execution → Functions are executed inside Docker containers, which are automatically started when required.
* Smart container management → Containers are paused after a period of inactivity and resumed when a new request is made, reducing resource consumption.
* HTTP API for remote execution → Each registered function can be called through an HTTP endpoint exposed by the system.
* Local scalability → The ability to run multiple functions simultaneously in isolated containers.