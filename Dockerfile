FROM mcr.microsoft.com/dotnet/sdk:10.0.401@sha256:e70cdb7f80b0348f5cb85f19a8f670fca061f033d57eed12fa003d58b0e06317 AS dotnet

FROM emscripten/emsdk:4.0.11@sha256:f8a157011b8fa61bdaab875bb1f0f08695229dffe086448d14b53538cae16bd3

ARG GODOT_EDITOR_URL=https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_mono_linux_x86_64.zip
ARG GODOT_EDITOR_SHA256=129f82db7bafd54ae14bb5bb284041c73860e8c7a009a3a026ca5e946cbff247

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

RUN curl --fail --location --retry 3 --output /tmp/godot.zip "$GODOT_EDITOR_URL" \
    && echo "$GODOT_EDITOR_SHA256  /tmp/godot.zip" | sha256sum --check --strict \
    && unzip -q /tmp/godot.zip -d /tmp/godot \
    && install -D -m 0755 \
        /tmp/godot/Godot_v4.7.2-stable_mono_linux_x86_64/Godot_v4.7.2-stable_mono_linux.x86_64 \
        /opt/godot/godot \
    && cp -a \
        /tmp/godot/Godot_v4.7.2-stable_mono_linux_x86_64/GodotSharp \
        /opt/godot/GodotSharp \
    && rm -rf /tmp/godot /tmp/godot.zip \
    && dotnet --info \
    && pip3 install --no-cache-dir 'scons==4.10.1' \
    && dotnet workload install wasm-tools --version 10.0.401.1

WORKDIR /godot

CMD ["bash"]
