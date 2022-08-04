#include "main.hh"

Oscil   oscil_1     {Oscil::Sine};
Oscil   oscil_2     {Oscil::Sine};

FilType filter_type {FilType::Lpf};

Gpio    status_led  {0, Gpio::Dir::Output};
Gpio    reset_led   {0, Gpio::Dir::Output};

Gpio    led_mux_s0  {0, Gpio::Dir::Output};
Gpio    led_mux_s1  {0, Gpio::Dir::Output};
Gpio    led_mux_s2  {0, Gpio::Dir::Output};

CD4051 led_mux      {&led_mux_s0, &led_mux_s1, &led_mux_s2};

// maps oscillator type to led mux channels
std::map<Oscil, std::uint8_t> oscil_1_map {{Oscil::Sine, 0}, {Oscil::Triangle, 0}, {Oscil::Square, 0}, {Oscil::Sawtooth, 0}};
std::map<Oscil, std::uint8_t> oscil_2_map {{Oscil::Sine, 0}, {Oscil::Triangle, 0}, {Oscil::Square, 0}, {Oscil::Sawtooth, 0}};

void set_oscillator_leds();
void poll_buttons();

int main()
{
    while(true)
    {

    }
}

void set_oscillator_leds()
{
    led_mux.set_channel(oscil_1_map[oscil_1]);
    led_mux.set_channel(oscil_2_map[oscil_2]);
}