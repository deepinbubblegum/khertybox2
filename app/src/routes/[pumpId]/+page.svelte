<script>
    import "../../app.css";
    import { page } from '$app/stores';
    import { onMount} from 'svelte'
    import axios from 'axios'
    import {CountUp} from 'countup.js'

	
	
// @ts-ignore
let PriceUnitList = null;
let PricePerUnit = 0.0;
let RealTimePrice = 0;
let stateCount = 0;
let type_fuel = "unknown";
let PreviewPrice =0
let PreviewUnit = 0
let PreviewTypeFuel ='/assets/images/type/'+ type_fuel + '.png'
let decimal_price = 2;
let decimal_unit = 3;
let unit=0;
let pumpnumber = 0;
let  pumpId  = $page.params.pumpId;

    if (Number(pumpId) * 1 !== 0) {
      pumpnumber = Number(pumpId);
    }
onMount(() => {
    var port = 5000;
    axios.defaults.baseURL = window.location.protocol + '//' + window.location.hostname + ':' + port;
    async function fetchData(){
                 try {
                    const res = await axios.get(`/${pumpnumber}`, {});
                    let msg = res.data;
                    if(msg["pump_id"]===pumpnumber){
                        console.log(msg)
                        if (msg['type'] === 1) 
                        {
                            if (stateCount >= 10) {//reset after 20 second 
                                stateCount = 0;
                                RealTimePrice=0;
                                PreviewPrice=0
                                PreviewUnit=0
                                type_fuel="unknown"
                            } else {
                                stateCount += 1;
                                console.log(stateCount)
                            }

                        } 
                        else if (msg["type"] === 2) 
                        {
                            PriceUnitList = msg['PriceUnitPeer'];
                            decimal_price = msg['decimal_preview_price'];
                            decimal_unit = msg['decimal_preview_unit'];
                            console.log('call');
                        } 
                        else if (msg['type'] === 3) 
                        {
                            RealTimePrice = msg['price'];
                            if (msg['grade_type']){
                                type_fuel = msg['grade_type'];
                                // @ts-ignore
                                PricePerUnit = PriceUnitList[type_fuel];
                            }
                            stateCount=0
                        } 
                        else if (msg['type'] === 4) 
                        {
                            type_fuel = msg['grade_type'];
                            PriceUnitList = msg['PriceUnitPeer'];
                            PricePerUnit = PriceUnitList[type_fuel];
                            console.log(`4 Update PricePerUnit : ${PricePerUnit}, type_fuel : ${type_fuel}`);
                            decimal_price = msg['decimal_preview_price'];
                            decimal_unit = msg['decimal_preview_unit'];
                        }
                        else if (msg['type'] === 5) 
                        {
                            PricePerUnit = msg['price_per_unit'];
                            type_fuel = msg['grade_type'];
                            unit = msg['transaction_vol'];
                            console.log('==============================');
                            console.log(msg);
                            console.log(`5 confirm PricePerUnit : ${PricePerUnit} Unit:${unit} `);
                        }
                        var countUp =new CountUp('PreviewPrice',RealTimePrice,{startVal:PreviewPrice,decimalPlaces:decimal_price,duration:3})
                        var countUp2 =new CountUp('PreviewUnit',RealTimePrice/PricePerUnit,{startVal:PreviewUnit,decimalPlaces:decimal_unit,duration:3})
                        PreviewTypeFuel = '/assets/images/type/'+ type_fuel + '.png';
                        if (!countUp.error) {
                            countUp.start();
                            countUp2.start();
                          } else {
                            console.error(countUp.error);
                          }

                    }



                } catch (e) {

                }


    }
    const interval= setInterval(()=>{
			fetchData()
      PreviewPrice=RealTimePrice
      PreviewUnit=RealTimePrice/PricePerUnit
      
		},2000) // 2 second per request

    return()=>clearInterval(interval)


})




  </script>

<div>
  <div class="min-w-max min-h-max">
    <img src={PreviewTypeFuel} alt="" />
        <div class="relative w-[1080px] h-[435px]">
          <img src="/assets/images/bg_1080x435.png" alt="aa">
          <span class="absolute bottom-16 left-40 w-[105px] inline-block self-center">
              <h1 class="text-center h-[118px] w-[103px] text-white text-[90px] antialiased font-sans p-0 font-medium leading-tight">
              {$page.params.pumpId}
             </h1>
          </span>
          <span class="absolute bottom-56 right-12">
             <h1 class="text-end align-middle text-white text-[165px] antialiased tracking-wide">
                <div id="PreviewPrice">0.00</div>
              </h1>
          </span>
          <span class="absolute bottom-4 right-12">
             <h1 class="text-end align-middle text-white text-[165px] antialiased tracking-wide">
                <div id="PreviewUnit">0.000</div>
              </h1>
          </span>
        </div>
      </div>
      
    </div>

