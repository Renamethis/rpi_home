import React from "react";
import styled from "styled-components";
import {WeatherIcons} from "./App";

export const WeatherInfoIcons = {
    sunset: "./icons/temp.svg",
    sunrise: "./icons/temp.svg",
    humidity: "./icons/humidity.svg",
    dust: "./icons/dust.svg",
    pressure: "./icons/pressure.svg",
    nh3: "./icons/nh3.png",
    oxidising: "./icons/oxidising.png",
    reducing: "./icons/reducing.png"
};
const Location = styled.span`
  margin: 15px auto;
  text-transform: capitalize;
  font-size: 28px;
  font-weight: bold;
`;
const Condition = styled.span`
  margin: 20px auto;
  text-transform: capitalize;
  font-size: 14px;
  & span {
    font-size: 28px;
  }
`;
const WeatherInfoLabel = styled.span`
  margin: 20px 25px 10px;
  text-transform: capitalize;
  text-align: start;
  width: 90%;
  font-weight: bold;
  font-size: 14px;
`;
const WeatherIcon = styled.img`
  width: 100px;
  height: 100px;
  margin: 5px auto;
`;
const WeatherContainer = styled.div`
  display: flex;
  width: 100%;
  margin: 30px auto;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

const WeatherInfoContainer = styled.div`
  display: flex;
  width: 90%;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
  flex-wrap: wrap;
`;
const InfoContainer = styled.div`
  display: flex;
  margin: 5px 10px;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
`;
const InfoIcon = styled.img`
  width: 36px;
  height: 36px;
`;
const InfoLabel = styled.span`
  display: flex;
  flex-direction: column;
  font-size: 14px;
  margin: 15px;
  & span {
    font-size: 12px;
    text-transform: capitalize;
  }
`;

const WeatherInfoComponent = (props) => {
    const {name, value} = props;
    const color = (value.value > value.limits[0] && value.value < value.limits[1]) ? 'green' : (value.value > value.limits[1]) ? 'red' : 'black';
    return (
        <InfoContainer>
            <InfoIcon src={WeatherInfoIcons[name]}/>
            <InfoLabel style={{ color: color }}>
                {Math.round(value.value) + " " + value.unit}
                <span>{name}</span>
            </InfoLabel>
        </InfoContainer>
    );
};
const WeatherComponent = (props) => {
    const {weather} = props;
    const d = new Date(weather.datetime);
    const isDay = (d.getHours() > 9 && d.getHours() < 17) ? "d": "n";
    const rain_factor = Math.round(11*((weather?.pressure.value)/1500)*(weather?.humidity.value/100));
    const normalized_factor = (rain_factor > 4 && rain_factor < 9) ? 4: rain_factor;
    const icon = (normalized_factor >= 10) ? normalized_factor + isDay : "0" + normalized_factor + isDay;
    return (
        <>
            <WeatherContainer>
                <Condition>
                    <span>{`${Math.floor(weather?.temperature.value)}°C`}</span>
                </Condition>
                <WeatherIcon src={WeatherIcons[icon]}/>
            </WeatherContainer>
            <Location>{`Moscow`}</Location>

            <WeatherInfoLabel>Weather Info</WeatherInfoLabel>
            <WeatherInfoContainer>
                <WeatherInfoComponent name={isDay == "d" ? "sunset" : "sunrise"}
                                      value={weather?.illumination}/>
                <WeatherInfoComponent name={"humidity"} value={weather?.humidity}/>
                <WeatherInfoComponent name={"dust"} value={weather?.dust}/>
                <WeatherInfoComponent name={"pressure"} value={weather?.pressure}/>
                <WeatherInfoComponent name={"nh3"} value={weather?.nh3}/>
                <WeatherInfoComponent name={"oxidising"} value={weather?.oxidising}/>
                <WeatherInfoComponent name={"reducing"} value={weather?.reducing}/>
            </WeatherInfoContainer>
        </>
    );
};

export default WeatherComponent;