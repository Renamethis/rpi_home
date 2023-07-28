import React, { useEffect, useState } from "react";
import styled from "styled-components";
import Axios from "axios";
import WeatherComponent from "./WeatherInfoComponent";

export const WeatherIcons = {
  "01d": "./icons/sunny.svg",
  "01n": "./icons/night.svg",
  "02d": "./icons/day.svg",
  "02n": "./icons/cloudy-night.svg",
  "03d": "./icons/cloudy.svg",
  "03n": "./icons/cloudy.svg",
  "04d": "./icons/perfect-day.svg",
  "04n": "./icons/cloudy-night.svg",
  "09d": "./icons/rain.svg",
  "09n": "./icons/rain-night.svg",
  "10d": "./icons/rain.svg",
  "10n": "./icons/rain-night.svg",
  "11d": "./icons/storm.svg",
  "11n": "./icons/storm.svg",
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 380px;
  padding: 20px 10px;
  margin: auto;
  border-radius: 4px;
  box-shadow: 0 3px 6px 0 #555;
  background: white;
  font-family: Montserrat;
`;

const AppLabel = styled.span`
  color: black;
  margin: 20px auto;
  font-size: 18px;
  font-weight: bold;
`;
const CloseButton = styled.span`
  padding: 2px 3px;
  background-color: black;
  border-radius: 50%;
  color: white;
  position: absolute;
`;

function App() {
  const [weather, updateWeather] = useState();
  useEffect(() => {
    const fetchWeather = async () => {
      const response = await Axios.get(
        'http://127.0.0.1:5000/get_last_entries',
      );
      let result = Object.fromEntries(response.data.slice(0,8).map(x => [x.field_name, x]));
      console.log(result)
      updateWeather(result);
    };
    fetchWeather();
  }, [])
  return (
    <Container>
      <AppLabel>React Weather App</AppLabel>
      {weather ? (
        <WeatherComponent weather={weather} city="Moscow" />
      ) : (
        <p> TEST </p>
      )}
    </Container>
  );
}

export default App;