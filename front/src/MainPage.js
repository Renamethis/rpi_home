import { useState, useEffect } from "react";
import Axios from "axios";
import { LineChartTransition } from "./LineChartTransition.tsx";
const QUERY_SIZE = 15;

export const MainPage = () => {
    const [weather, updateWeather] = useState([]);
    useEffect(() => {
      const fetchWeather = async () => {
        const response = await Axios.get(
          process.env.REACT_APP_BASE_URL + "/get_last_entries/" + QUERY_SIZE,
        );
        let result = [];
        for(const [key, value] of response.data.entries()) {
          let entry = {
            x: key,
          };
          entry['datetime'] = String(value['datetime'])
          for(const key of Object.keys(value)) {
            if(key != "datetime")
              entry[key] = value[key].value
          }
          result.push(entry);
        }
        updateWeather(result);
      };
      fetchWeather();
    }, [])

    return (
        <LineChartTransition entries={QUERY_SIZE} data={weather} width="400" height="500"/>
    );
}