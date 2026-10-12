FROM mcr.microsoft.com/dotnet/sdk:10.0.401@sha256:e70cdb7f80b0348f5cb85f19a8f670fca061f033d57eed12fa003d58b0e06317 AS dotnet

FROM emscripten/emsdk:4.0.11@sha256:f8a157011b8fa61bdaab875bb1f0f08695229dffe086448d14b53538cae16bd3

ENV DEBIAN_FRONTEND=noninteractive \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_NOLOGO=1 \
    DOTNET_ROOT=/usr/share/dotnet \
    PATH=/usr/share/dotnet:/root/.dotnet/tools:${PATH}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        fontconfig \
        git \
        libasound2-dev \
        libdbus-1-dev \
        libfontconfig1-dev \
        libgl1-mesa-dev \
        libpulse-dev \
        libudev-dev \
        libwayland-dev \
        libx11-dev \
        libxcursor-dev \
        libxi-dev \
        libxinerama-dev \
        libxkbcommon-dev \
        libxrandr-dev \
        pkg-config \
        python3 \
        python3-pip \
        unzip \
        zip \
    && rm -rf /var/lib/apt/lists/*

ENV DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1

COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet

RUN dotnet --info \
    && pip3 install --no-cache-dir 'scons==4.10.1' \
    && dotnet workload install wasm-tools --version 10.0.401.1

WORKDIR /godot

CMD ["bash"]
