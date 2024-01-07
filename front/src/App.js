import styled from "styled-components";
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from 'react-router-dom';
import WeatherComponent from "./WeatherInfoComponent";
//import ConnectedScatterplot from './D3Component.tsx';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MainPage } from './MainPage.js'
import { Menu, Layout } from "antd";
import './App.scss'

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  margin: 0 0 0 0;
  align-items: center;
  border-radius: 4px;
  box-shadow: 0 3px 6px 0 #555;
  background: white;
  position: relative;
`;

const NavigationMenu = ({ mode }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const handleNavigate = (e) => {
    navigate((e.key == "metrics" ? "/": "weather"));
  }
  return (
    <Menu onClick={handleNavigate} mode={mode} defaultSelectedKeys={(location.pathname == "/weather") ? "current" : "metrics"}>
      <Menu.Item key="metrics">Metrics</Menu.Item>
      <Menu.Item key="current">CurrentState</Menu.Item>
    </Menu>
  );
};

function getWindowDimensions() {
  const { innerWidth: width, innerHeight: height } = window;
  return {
    width,
    height
  };
}

function useWindowDimensions() {
  const [windowDimensions, setWindowDimensions] = useState(getWindowDimensions());

  useEffect(() => {
    function handleResize() {
      setWindowDimensions(getWindowDimensions());
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowDimensions;
}

const NavigationContent = ({width, height}) => {
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const [transitionStage, setTransistionStage] = useState("fadeIn");
  useEffect(() => {
    if (location !== displayLocation) setTransistionStage("fadeOut");
  }, [location, displayLocation]);
  return (
    <div style={{
           display:"flex",
           flexDirection:"column",
           alignItems:"center",
           height:height - 65
         }}
         className={`${transitionStage}`}
         onAnimationEnd={() => {
           if (transitionStage === "fadeOut") {
             setTransistionStage("fadeIn");
             setDisplayLocation(location);
           }
         }}>
          <Container>
            <Routes>
              <Route path="/" element={<MainPage width={width} height={height} transitionStage={transitionStage}/>} />
              <Route path="/weather" element={<WeatherComponent transitionStage={transitionStage}/>} />
            </Routes>
          </Container>
    </div>
  );
};

function App() {
  const { height, width } = useWindowDimensions();
    return (
      <div style={{width: width, height: height}} scroll="no">
        <BrowserRouter>
              <Layout>
                <Layout.Header className="nav-header">
                      <div className="leftMenu">
                        <NavigationMenu mode={"horizontal"} />
                      </div>
                </Layout.Header>
              </Layout>
              <NavigationContent width={width} height={height}></NavigationContent>
        </BrowserRouter>
        </div>
    );
}

export default App;