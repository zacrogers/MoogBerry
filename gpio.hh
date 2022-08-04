#pragma once
#include <cstdint>

class Gpio
{
public:
    enum class Dir
    {
        Input = 0,
        Output
    };

    Gpio(std::uint8_t pin_num, Dir dir);
    void set_dir(Dir dir);
    void set();
    void clear();
    void toggle();
    std::uint16_t read();

private:
    std::uint8_t m_pin_num;
};
