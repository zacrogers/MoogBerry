#pragma once
#include <cstdint>
#include <map>

#include "gpio.hh"
#include "mcp3008.hh"

enum class Oscil
{
    Sine = 0,
    Square,
    Triangle,
    Sawtooth
};

enum class FilType
{
    Hpf = 0,
    Lpf,
    Bpf
};

class CD4051
{
public:
    CD4051(Gpio *s0, Gpio *s1, Gpio *s2) : m_s0{s0}, m_s1{s1}, m_s2{s2} {};
    void set_channel(std::uint8_t channel);

private:
    Gpio *m_s0;
    Gpio *m_s1;
    Gpio *m_s2;
};