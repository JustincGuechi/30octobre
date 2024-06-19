document.addEventListener('DOMContentLoaded', function() {
    // Récupérer les données des usagers depuis le fichier JSON
    fetch('static/Json/15042024140000C1.usager.json')
        .then(response => response.json())
        .then(data => {
            // Compter le nombre d'occurrences de chaque type d'usager
            const usagersCount = {};
            data.Data.forEach(item => {
                const usagerType = item.Usager;
                usagersCount[usagerType] = (usagersCount[usagerType] || 0) + 1;
            });

            // Générer le graphique en barres
            generateBarChart(usagersCount);
        })
        .catch(error => console.error('Erreur lors du chargement des données des usagers:', error));

    fetch('static/Json/15042024140000C1.interaction.json')
        .then(response => response.json())
        .then(data => {
            // Extraire les différents types d'interactions
            const interactionTypes = new Set();
            data.Data.forEach(interaction => {
                if (interaction.Interaction) {
                    interactionTypes.add(interaction.Interaction);
                }
            });

            // Générer le graphique en camembert avec les données d'interaction
            generatePieChart(interactionTypes, data);
        })
        .catch(error => console.error('Erreur lors du chargement des données des interactions:', error));
});

function generateBarChart(usagersCount) {
    const labels = Object.keys(usagersCount);
    const data = Object.values(usagersCount);

    const ctx = document.getElementById('barChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nombre d\'usagers',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function generatePieChart(interactionTypes, data) {
    // Définir un objet pour stocker le nombre d'occurrences de chaque type d'interaction
    const interactionCount = {};

    // Parcourir chaque type d'interaction
    interactionTypes.forEach(interactionType => {
        // Compter le nombre d'occurrences de cet type d'interaction dans les données d'interaction
        const count = data.Data.filter(interaction => interaction.Interaction === interactionType).length;

        // Stocker le nombre d'occurrences dans l'objet interactionCount
        interactionCount[interactionType] = count;
    });

    // Récupérer les labels et les données pour le graphique en donut
    const labels = Object.keys(interactionCount);
    const dataCount = Object.values(interactionCount);

    // Générer le graphique en donut
    const ctx = document.getElementById('pieChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nombre d\'interactions',
                data: dataCount,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                    'rgba(255, 159, 64, 0.5)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Récupérer les données d'interactions depuis le fichier JSON
    fetch('interactions_counts.json')
        .then(response => response.json())
        .then(interactionCounts => {
            // Extraire les noms des fichiers et les nombres d'interactions
            const filenames = Object.keys(interactionCounts);
            const counts = Object.values(interactionCounts);

            // Générer le graphique
            generateLineChart(filenames, counts);
        })
        .catch(error => console.error('Erreur lors du chargement des données:', error));
});

function generateLineChart(filenames, counts) {
    const ctx = document.getElementById('lineChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: filenames,
            datasets: [{
                label: 'Nombre d\'interactions',
                data: counts,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

