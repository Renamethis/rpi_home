#!/bin/bash

VER="2835"

sudo rmmod spi_bcm${VER}

sudo modprobe spi_bcm${VER}