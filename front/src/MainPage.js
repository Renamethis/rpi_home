import Axios from "axios";
import { useState, useRef, useEffect } from 'react';
import { LineChartTransition } from "./LineChartTransition.tsx";
import * as d3 from "d3";

const QUERY_SIZE = 15;
const SLIDE_FACTOR = 10;

export const MainPage = ({width, height, transitionStage}) => {
    const [weather, updateWeather] = useState([]);
    const startpointref = useRef();
    const [currentPointer, updateCurrentPointer] = useState(0);
    const [currentScope, updateCurrentScope] = useState(0);
    const [previousScope, updatePreviousScope] = useState(0);

    useEffect(() => {
      const fetchWeather = async () => {
            if(currentScope*2*QUERY_SIZE == weather.length) { // TODO: FIX
              const response = await Axios.get(
                process.env.REACT_APP_BASE_URL +
                  "/get_last_entries/" +
                  Math.floor((currentPointer + 1.8*QUERY_SIZE)/(2*QUERY_SIZE)) +
                  "/" + 2*QUERY_SIZE,
              );
              let result = [];
              for(const [key, value] of response.data.entries()) {
                let entry = {
                  x: key + Math.floor((currentPointer + 1.8*QUERY_SIZE)/(2*QUERY_SIZE))*(2*QUERY_SIZE)
                };
                entry['datetime'] = String(value['datetime'])
                for(const key of Object.keys(value)) {
                  if(key != "datetime")
                    entry[key] = value[key].value
                }
                result.push(entry);
              }
              result = weather.concat(result)
              updateWeather(result);
            }
    }
      fetchWeather();
    }, [currentScope]);

    const handleStart = (event) => {
      const t = d3.pointers(event, this);
      startpointref.current = t;
    };

    const handleMove = (event) => {
      const t = d3.pointers(event, this);
      const pointx = t[0][0];
      const pointy = t[0][1];
      if(startpointref.current) {
        const point2 = startpointref.current[0];
        let xDiff = pointx - point2[0];
        const yDiff = pointy - point2[1];
        if (Math.abs( xDiff ) > Math.abs( yDiff )) {
            if(Math.abs(xDiff) > 0.3*width) {
              startpointref.current = undefined;
              xDiff = xDiff/Math.abs(xDiff)*0.3*width;
            }
            const number = Math.floor((xDiff/width) * SLIDE_FACTOR);
            if(currentPointer + number > 0)
              updateCurrentPointer(currentPointer + number);
            else
            updateCurrentPointer(0);
        }
      }
    };

    const handleEnd = (event) => {
      startpointref.current = undefined;
      const newScope = Math.floor((currentPointer + 1.8*QUERY_SIZE)/(2*QUERY_SIZE))
      if(newScope != previousScope)
        updateCurrentScope(newScope);
      updatePreviousScope(currentScope);
    };

    return (
      <>
      {weather.length && <div onMouseMove={handleMove} onTouchStart={handleStart} onTouchMove={handleMove} onMouseDown={handleStart} onMouseUp={handleEnd} onTouchEnd={handleEnd}>
        {(transitionStage != "fadeOut") && <LineChartTransition currentScope={currentScope} currentPointer={currentPointer} entries={QUERY_SIZE} data={weather} width={width} height={height}/>}
      </div>}
      </>
    );
}