#pragma once

class MCP3008
{
public:
    MCP3008();
    std::uint16_t read(std::uint8_t channel);

private:
    const char *device = "/dev/spidev0.0";
};