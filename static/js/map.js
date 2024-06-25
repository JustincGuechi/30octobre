console.log("map.js chargé");

// Fonction pour charger les données JSON
async function chargerDonneesJson(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Erreur lors du chargement des données JSON :", error);
    }
}

// Fonction principale pour initialiser les données
async function init_data() {
    const timerElement = document.getElementById('timer_totaleseconde');
    const day_actual_element = document.getElementById('day_actual');
    //console.log("timerElement :", timerElement);
    //console.log("day_actual_element :", day_actual_element);
    if (timerElement && day_actual_element) {
        let seconds = parseInt(timerElement.textContent, 10);
        let hours = Math.floor(seconds / 3600);
        const data_json = `/get_json_for_plan?hour=${hours}&day=${day_actual_element.textContent}`;
        
        // Charger les données JSON
        const data1 = await chargerDonneesJson(data_json);

        // Afficher les données JSON dans la console
        console.log("Données JSON chargées :", data1);

        // Démarrer l'animation
        startAnimation(data1);
    }
}

// Fonction pour démarrer l'animation
function startAnimation(data) {
    function step() {
        update_canvas(data);
        requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// Fonction pour mettre à jour le canvas
function update_canvas(data) {
    const timerElement = document.getElementById('timer_totaleseconde');
    let seconds = parseFloat(timerElement.textContent);
    if (seconds) {
        dessinerPoints(data, seconds);
    }
}
function floatsAreClose(a, b, epsilon = 1) {
    return Math.abs(a - b) < epsilon;
}

// Fonction pour dessiner les points sur le canvas
function dessinerPoints(data, elapsedTime) {
    const canvas = document.getElementById('canvas_plan');
    const ctx = canvas.getContext('2d');
    canvas.width = 992;
    canvas.height = 921;

    // Effacer le canvas avant de dessiner
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Écrire "Omographie" en haut à gauche en rouge
    ctx.font = 'bold 20px Arial';
    ctx.fillStyle = 'red';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('Reproduction dans la vie réel active', 10, 10);

    // Fonction pour dessiner un point sur le canvas
    function drawPoint(x, y, color) {
        // Dessiner la boîte autour de l'objet correspondant
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.fillStyle = color; // couleur du point
        ctx.fill();
        ctx.closePath();
    }

    //console.log("Dessin des points sur le canvas...");
    data.forEach(item => {
        const timeCodeDebut = item.Time_code_debut;

        item.data.forEach(trajectory => {
            let color = "black"; // Default color
            if (trajectory.Usager === "car") {
                color = "blue";
            } else if (trajectory.Usager === "person") {
                color = "red";
            } else if (trajectory.Usager === "bicycle") {
                color = "green";
            } else if (trajectory.Usager === "bus") {
                color = "yellow";
            }
            trajectory.data.forEach(point => {
                const pointTime = timeCodeDebut + point.time / 1000; // Convertir le temps du point en secondes absolues
                //console.log("pointTime", pointTime);
                //console.log("elapsedTime", elapsedTime);
                if ( floatsAreClose(elapsedTime, pointTime)&& point.lat !== -1 && point.lon !== -1) {
                    
                    const x = point.lat;
                    const y = point.lon;
                    drawPoint(x, y, color);
                }
            });
        });
    });
}

// Appeler la fonction init_data pour démarrer le processus