import ReactDOM from "react-dom/client";
import 'bootstrap/dist/css/bootstrap.min.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./pages/Layout";
import Home from "./pages/Home"
import MyAds from "./pages/MyAds";
import CreateAd from "./pages/CreateAd";
import CreateOrder from "./pages/CreateOrder";
import MyOrders from "./pages/MyOrders";
import Wallet from "./pages/Wallet";
import OrderDetails from "./pages/OrderDetails";
import Deposit from "./pages/Deposit";
import Withdrawal from "./pages/Withdrawal";
import Auth from "./pages/AuthPage";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="/myads" element={<MyAds />}/>
          <Route path="myads/create" element={<CreateAd />} />
          <Route path="createOrder/" element={<CreateOrder />} />
          <Route path="/myOrders" element={<MyOrders/>}/>
          <Route path="/wallet" element={<Wallet/>}/>
          <Route path="/myOrders/order" element={<OrderDetails/>}/>
          <Route path="/deposit/:id" element={<Deposit />}/>
          <Route path="/withdrawal/:id" element={<Withdrawal />}/>
        </Route>
        <Route path="/auth" element={<Auth/>}/>
      </Routes>
    </BrowserRouter>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);