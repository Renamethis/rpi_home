import styled from "styled-components";
import WeatherComponent from "./WeatherInfoComponent";
//import ConnectedScatterplot from './D3Component.tsx';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MainPage } from './MainPage.js'
import './App.css'
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
  width: 100%;
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
    return (
      <Container>
        <AppLabel>Environment Weather App</AppLabel>
        <BrowserRouter>
            <Routes>
              <Route path="/" element={<MainPage/>} />
              <Route path="/weather" element={<WeatherComponent/>} />
            </Routes>
        </BrowserRouter>
      </Container>
    );
}

export default App;