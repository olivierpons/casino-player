from setuptools import setup, Extension

setup(
    name="casino-player",
    version="1.0",
    description="Roulette player statistics tracker",
    ext_modules=[Extension("casino_player", sources=["roulette-player.c"])],
)
