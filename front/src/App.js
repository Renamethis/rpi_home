import React, { useEffect, useState } from "react";
import styled from "styled-components";
import Axios from "axios";
import WeatherComponent from "./WeatherInfoComponent";
import ConnectedScatterplot from './D3Component.tsx';

export const WeatherIcons = {
  "01d": "./icons/perfect-day.svg",
  "01n": "./icons/night.svg",
  "02d": "./icons/sunny.svg",
  "02n": "./icons/night.svg",
  "03d": "./icons/cloudy.svg",
  "03n": "./icons/cloudy-night.svg",
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

const QUERY_SIZE = 5;
function App() {
  const [weather, updateWeather] = useState([]);
  useEffect(() => {
    const fetchWeather = async () => {
      const response = await Axios.get(
        process.env.REACT_APP_BASE_URL + "/get_last_entries/5",
      );
      let result = [];
      for(const [key, value] of response.data.entries()) {
        result.push({
          x: key,
          y: value.temperature.value, // Temp
        });
      }
      updateWeather(result);
    };
    fetchWeather();
  }, [])
  return (
    <Container>
      <AppLabel>Environment Weather App</AppLabel>
      <ConnectedScatterplot data={weather} width="400" height="500"></ConnectedScatterplot>
    </Container>
  );
}

export default App;