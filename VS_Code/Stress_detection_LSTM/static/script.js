// =========================================
// SAMPLE DATA
// =========================================

const labels = [
    "0","10","20","30","40",
    "50","60","70","80","90"
];

const temperatureData = [30,31,31,32,33,34,35,36,36,37];
const currentData = [0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.7,0.8,0.9];

// =========================================
// CHART
// =========================================

const ctx = document.getElementById('sensorChart');

const chart = new Chart(ctx, {

    type:'line',

    data:{

        labels:labels,

        datasets:[

            {
                label:'Temperature (°C)',
                data:temperatureData,
                borderColor:'red',
                tension:0.4
            },

            {
                label:'Current (A)',
                data:currentData,
                borderColor:'lime',
                tension:0.4
            }

        ]
    },

    options:{

        responsive:true,

        plugins:{
            legend:{
                labels:{
                    color:'white'
                }
            }
        },

        scales:{

            x:{
                ticks:{
                    color:'white'
                }
            },

            y:{
                ticks:{
                    color:'white'
                }
            }
        }
    }
});

// =========================================
// DEFAULT VALUES
// =========================================

let sampleStress = 18;

// =========================================
// UPDATE UI
// =========================================

function updateUI(data){

    document.getElementById("temp").innerHTML =
        data.temperature + " °C";

    document.getElementById("current").innerHTML =
        data.current + " A";

    document.getElementById("vibration").innerHTML =
        data.vibration;

    document.getElementById("stressScore").innerHTML =
        data.stress_score + "%";

    document.getElementById("status").innerHTML =
        data.status;

    const statusBox =
        document.getElementById("statusBox");

    statusBox.innerHTML =
        data.status.toUpperCase();

    statusBox.className = "status-box";

    // COLORS

    if(data.status === "Normal"){

        statusBox.classList.add("normal");

    }else if(data.status === "Warning"){

        statusBox.classList.add("warning");

    }else{

        statusBox.classList.add("critical");
    }

    // ADD GRAPH VALUES

    labels.push(new Date().toLocaleTimeString());

    temperatureData.push(data.temperature);
    currentData.push(data.current);

    if(labels.length > 15){

        labels.shift();
        temperatureData.shift();
        currentData.shift();
    }

    chart.update();
}

// =========================================
// FETCH LIVE DATA
// =========================================

async function fetchData(){

    try{

        const response =
            await fetch('/get_data');

        const data =
            await response.json();

        updateUI(data);

    }catch(error){

        console.log("Using sample data...");

        // RANDOM SAMPLE DATA

        sampleStress += Math.floor(Math.random()*5);

        if(sampleStress > 95){
            sampleStress = 18;
        }

        let sampleData = {

            temperature:
                (30 + Math.random()*7).toFixed(1),

            current:
                (0.3 + Math.random()*0.6).toFixed(2),

            vibration:
                Math.random() > 0.7 ? "YES" : "NO",

            stress_score:
                sampleStress,

            status:
                sampleStress < 30
                ? "Normal"
                : sampleStress < 70
                ? "Warning"
                : "Critical"
        };

        updateUI(sampleData);
    }
}

// =========================================
// UPDATE EVERY 2 SECONDS
// =========================================

setInterval(fetchData, 2000);