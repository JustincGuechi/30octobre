$(document).ready(function () {
  var userData = []; // Variable pour stocker les données d'usager
  var interactionData; // Variable pour stocker les données d'interaction
  var load = false;
  const cameras = [
    "C1_Thiers",
    "C2_Gray",
    "C3_AVIA",
    "C4_Strasbourg",
    "C5_Boulangerie",
    "C6_Voltaire",
    "C7_Carnot",
  ]; // Liste des caméras
  let selectedCamera = cameras[0]; // Caméra sélectionnée par défaut
  var dayHour = "00h-01h"; // Heure par défaut
  var debut;
  var hour;
  spinner();

  

  function afficherUsagers(userData) {
    // Création des options du menu déroulant pour les utilisateurs
    var utilisateurs = {};
    userData.forEach(function (obj) {
      if (!utilisateurs[obj.Usager]) {
        utilisateurs[obj.Usager] = true;
        $('#userTypeSelect').append('<option value="' + obj.Usager + '">' + obj.Usager + '</option>');
      }
    });

    // Gestionnaire d'événement pour le changement de sélection dans le menu déroulant des utilisateurs
    $('#userTypeSelect').change(function () {
      var selectedUsager = $(this).val();
      var selectedInteraction = $('#interactionSelect').val();
      filterAndRenderInteractions(selectedUsager, selectedInteraction);
    });

    // Affichage initial des interactions avec toutes les données d'usager
    //filterAndRenderInteractions('', '');
  }

  function afficherID(userData) {
$('#userIDSelect').empty();
    // Création des options du menu déroulant pour les utilisateurs
    var utilisateurs = {};
    userData.forEach(function (obj) {

        utilisateurs[obj.Usager] = true;
        $('#userIDSelect').append('<option value="' + obj.ID + '">' + obj.ID + '</option>');

    });
  }

  // Chargement des interactions depuis l'API Flask
 async function affichage_interaction_avec_data(response, data_minute_sec) {
    console.log("date_time_minute : ", data_minute_sec);
    interactionData = response; // Assignation des données à la variable interactionData

    // Création des options du menu déroulant pour les interactions
    var interactions = {};
    interactionData.forEach(function (obj) {
        if (!interactions[obj.interaction]) {
            interactions[obj.interaction] = true;
            $('#interactionSelect').append('<option value="' + obj.interaction + '">' + obj.interaction + '</option>');
        }
    });

    // Gestionnaire d'événement pour le changement de sélection dans le menu déroulant des interactions
    $('#interactionSelect').change(function () {
        var selectedInteraction = $(this).val();
        var selectedUsager = $('#userTypeSelect').val();
        filterAndRenderInteractions(selectedUsager, selectedInteraction, data_minute_sec);
    });

    // Affichage initial des interactions avec tous les time_codes
    renderFilteredInteractions(interactionData, data_minute_sec);
};

  // Fonction pour filtrer les interactions en fonction des utilisateurs et des interactions sélectionnés
function filterAndRenderInteractions(userType, interactionType, data_minute_sec) {
    console.log("Filtering interactions for user type:", userType, "and interaction type:", interactionType);

    var filteredData = interactionData.filter(function (obj) {
        return (obj.interaction === interactionType || !interactionType) &&
               (obj.id.includes(userType) || !userType);
    });

    renderFilteredInteractions(filteredData, data_minute_sec);
}


  // Fonction pour afficher les interactions filtrées en fonction de l'interaction sélectionnée
  function renderFilteredInteractions(data, data_minute_sec) {
    console.log("timerElement :", data_minute_sec);
    console.log("get dayhour", dayHour);
    // Étape 1 : Séparer la chaîne sur les caractères de soulignement
    var parts = dayHour.split("_");

    // Étape 2 : Accéder à l'élément qui contient l'heure
    var hourPart = parts[3]; // "09"

    // Étape 3 : Extraire la partie numérique (dans ce cas, c'est déjà numérique)
    var hour = parseInt(hourPart, 10) - 1; // 9

    time = parseInt(data_minute_sec["minutes"]) * 60 + parseInt(data_minute_sec["seconds"]) + hour * 3600;
    var interactionsHtml = "<h2>Interactions filtrées</h2>";
    data.forEach(function (obj) {
      timeobjstart = obj.start_time + time;
      timeobjstop = obj.end_time + time;

      // Calculer heures, minutes, et secondes
      var hours1 = Math.floor(timeobjstart / 3600);
      var minutes1 = Math.floor((timeobjstart % 3600) / 60);
      var seconds1 = parseInt(timeobjstart % 60);

      // Formater pour avoir toujours deux chiffres
      var hoursFormatted1 = hours1.toString().padStart(2, '0');
      var minutesFormatted1 = minutes1.toString().padStart(2, '0');
      var secondsFormatted1 = seconds1.toString().padStart(2, '0');


      interactionsHtml += '<div class="interaction-container">';
      interactionsHtml += '<form class="interaction-form">';
      interactionsHtml += "<ul>";

      interactionsHtml +=
        '<li class="time-code" data-index="' +
        obj.id_interaction +
        '">Heure de debut : ' + hoursFormatted1 + ":" + minutesFormatted1 + ":" + secondsFormatted1 + " - ";
      // Calculer heures, minutes, et secondes
      var hours = Math.floor(timeobjstop / 3600);
      var minutes = Math.floor((timeobjstop % 3600) / 60);
      var seconds = parseInt(timeobjstop % 60);

      // Formater pour avoir toujours deux chiffres
      var hoursFormatted = hours.toString().padStart(2, '0');
      var minutesFormatted = minutes.toString().padStart(2, '0');
      var secondsFormatted = seconds.toString().padStart(2, '0');

      var totalhours = hours - hours1;
      var totalminutes = minutes - minutes1;
      var totalseconds = seconds - seconds1;

      var totalhoursFormatted = totalhours.toString().padStart(2, '0');
      var totalminutesFormatted = totalminutes.toString().padStart(2, '0');
      var totalsecondsFormatted = totalseconds.toString().padStart(2, '0');

      interactionsHtml += "Heure de fin :" + hoursFormatted + ":" + minutesFormatted + ":" + secondsFormatted;
      interactionsHtml += " Temps total :" + totalhoursFormatted + ":" + totalminutesFormatted + ":" + totalsecondsFormatted + " id interaction : " + obj.id_interaction + "</li>";

        "</li>";
      interactionsHtml += '<div class="interaction-details-container">';
      interactionsHtml += '<div class="interaction-details">';
      interactionsHtml +=
        '<li class="time-code-debut-time">Heure de début: <input type="text" name="time-code-debut" value="' +
        hoursFormatted1 + ":" + minutesFormatted1 + ":" + secondsFormatted1 +
        '"></li>';
      interactionsHtml +=
        '<li class="time-code-fin-time">Heure de fin: <input type="text" name="time-code-fin" value="' +
        hoursFormatted + ":" + minutesFormatted + ":" + secondsFormatted +
        '"></li>';
      interactionsHtml +=
        '<li class="interaction-type">Interaction: <input type="text" name="interaction" value="' +
        obj.interaction +
        '"></li>';
      interactionsHtml +=
        '<li class="interaction-comment">Commentaire: <input type="text" name="commentaire" value="' +
        (obj.commentaire || "") +
        '"></li>';
        if(obj.valide == "Valide"){
          var valide = "Validé";
        }else{
          var valide = "Non validé";
        }
        interactionsHtml += "<li>" + valide+ "</li>";
      // Affichage des autres informations sur l'interaction
      interactionsHtml += "<li>ID: " + obj.id_interaction + "</li>";
      interactionsHtml += "<li>Utilisateur(s): ";
      if (obj.id && Array.isArray(obj.id)) {
        // Vérifier si obj.User est défini et est un tableau
        obj.id.forEach(user => {
          interactionsHtml += user + ", ";
        }
        );

        interactionsHtml = interactionsHtml.slice(0, -2); // Remove the last comma and space
      } else {
        interactionsHtml += "Non spécifié";
      }
      interactionsHtml += "</li>";
      interactionsHtml += "</div>";
      interactionsHtml += '<div class="button-container">'; // Ajout de la classe pour les boutons
      interactionsHtml +=
        '<button type="button" class="valid-btn">Valider</button>';
      interactionsHtml +=
        '<button type="button" class="modifier-btn" value="' +
        obj.ID +
        '">Modifier</button>';
      interactionsHtml +=
        '<button type="button" class="supprimer-btn">Supprimer</button>';
      interactionsHtml += "</div>"; // Fin de la div pour les boutons
      interactionsHtml += "</div>";
      interactionsHtml += "</ul>";
      interactionsHtml += "</form>";
      interactionsHtml += "</div>";
      console.log(obj.ID);
    });
    $("#filteredInteractions").html(interactionsHtml);

    // Event listener for time code click
    $(".time-code").click(function () {
      var index = $(this).data("index");
      var detailsContainer = $(this).siblings(".interaction-details-container");

      // Toggle visibility of details
      detailsContainer.slideToggle();
    });

    $(".valid-btn").click(function () {
      console.log("Valide button clicked");

      // Récupérer l'ID de l'interaction à partir de l'attribut data
      var interactionId = $(this)
        .closest(".interaction-container")
        .find(".time-code")
        .data("index");


      // Modifier le statut de l'interaction à "Valide"
      $.ajax({
        url: "/update_interaction_valider",
        method: "GET",
        data: {
          Id: interactionId,
          statut: "Valide",
          camera: cameraSelect.value,
          dayHour: dayHour
        },
        success: function (response) {
          alert("Validé avec succès");
          console.log("Statut mis à jour avec succès !");
          // Actualiser la page ou afficher un message de réussite, etc.
        },
        error: function (xhr, status, error) {
          alert("Echec de la validation");

          console.error("Erreur lors de la mise à jour du statut :", error);
          console.error("Status:", status);
          console.error("Response text:", xhr.responseText);
          // Afficher un message d'erreur à l'utilisateur, etc.
        },
      });
    });
    
    

    // Event listener for modifier button
    $(".modifier-btn").click(function () {
      var interactionId = $(this)
        .closest(".interaction-container")
        .find(".time-code")
        .data("index");
      var $interactionContainer = $(this).closest(".interaction-container");

      var interactionToUpdate = {
        ID: interactionId,
        Time_code_debut: $interactionContainer.find('input[name="time-code-debut"]').val(),
        Time_code_fin: $interactionContainer.find('input[name="time-code-fin"]').val(),
        Interaction: $interactionContainer.find('input[name="interaction"]').val(),
        Commentaire: $interactionContainer.find('input[name="commentaire"]').val(),
        Validé: $interactionContainer.find('input[name="statut"]').val(),
    };
      console.log("interactionToUpdate", interactionToUpdate);
      time = parseInt(data_minute_sec["minutes"]) * 60 + parseInt(data_minute_sec["seconds"]) + hour * 3600;
      timecode = interactionToUpdate.Time_code_debut.split(":");
      console.log(timecode);

      start_time_update = parseInt(timecode[0]) * 3600 + parseInt(timecode[1]) * 60 + parseInt(timecode[2]) - time;
      timecode = interactionToUpdate.Time_code_fin.split(":");
      stop_time_update = parseInt(timecode[0]) * 3600 + parseInt(timecode[1]) * 60 + parseInt(timecode[2]) - time;
     
      console.log("start_time_update", start_time_update);
      console.log("stop_time_update", stop_time_update);
      const day_hour = document.getElementById("day_hour");
      var heureActuelleFormatted = parseInt(day_hour.textContent)// Ajoute un zéro devant si nécessaire et prend les deux derniers chiffres
      
    

      // Envoyer les données mises à jour au backend via les paramètres de requête dans l'URL
      $.ajax({
        url: "/update_interaction_modifier",
        method: "GET",
        data: {
          hour:heureActuelleFormatted,
          dayHour: dayHour,
          camera: cameraSelect.value,
          Id: interactionId,
          Time_code_debut: start_time_update,
          Time_code_fin: stop_time_update,
          interaction: interactionToUpdate.Interaction,
          commentaire: interactionToUpdate.Commentaire,
          statut: interactionToUpdate.Validé,
        },
        success: function (response) {
          alert("Modifier avec succès");
          console.log("Données mises à jour avec succès !");
          // Actualiser la page ou afficher un message de réussite, etc.
        },
        error: function (xhr, status, error) {
          alert("echec de la modification");
          console.error("Erreur lors de la mise à jour des données :", error);
          // Afficher un message d'erreur à l'utilisateur, etc.
        },
      });
    });

    // Event listener for supprimer button
    $(".supprimer-btn").click(function () {
      // Récupérer l'ID de l'interaction à partir de l'attribut data
      var interactionId = $(this)
        .closest(".interaction-container")
        .find(".time-code")
        .data("index");

      // Envoyer la demande de suppression au backend
      $.ajax({
        url: "/delete_interaction",
        method: "GET",
        data: {
          Id: interactionId,
          dayHour: dayHour,
          camera: cameraSelect.value
        },
        success: function (response) {
          alert("Supprimé avec succès");

          console.log("Interaction supprimée avec succès !");
          // Actualiser la page ou afficher un message de réussite, etc.
        },
        error: function (xhr, status, error) {
          alert("Echec de la suppression");

          console.error(
            "Erreur lors de la suppression de l'interaction :",
            error
          );
          // Afficher un message d'erreur à l'utilisateur, etc.
        },
      });
    });
    $(".creer-btn").click(function () {
      console.log("Créer button clicked");
      // Récupérer les valeurs des champs de texte
      const startTime = document.querySelector('input[name="newstart_time"]').value;
      const endTime = document.querySelector('input[name="newend_time"]').value;
      const interaction = document.querySelector('input[name="newinteraction"]').value;
      const commentaire = document.querySelector('input[name="newcommentaire"]').value;
      const valide = document.querySelector('input[name="newvalide"]').checked;
  
      // Récupérer les valeurs des checkboxes sélectionnées
      const selectedValues = Array.from(document.querySelectorAll('#list3 .items input[type="checkbox"]:checked'))
                                  .map(checkbox => checkbox.value);
  
      // Préparer les données pour la requête AJAX
      const data = {
          start_time: startTime,
          end_time: endTime,
          interaction: interaction,
          selected_values: selectedValues,
          commentaire: commentaire,
          valide: valide
      };
      console.log("data", data);

      time = parseInt(data_minute_sec["minutes"]) * 60 + parseInt(data_minute_sec["seconds"]) + hour * 3600;
      timecode =  data["start_time"].split(":");
      console.log(timecode);
  
      start_time_update = parseInt(timecode[0]) * 3600 + parseInt(timecode[1]) * 60 + parseInt(timecode[2]) - time;
      timecode = data["end_time"].split(":");
      stop_time_update = parseInt(timecode[0]) * 3600 + parseInt(timecode[1]) * 60 + parseInt(timecode[2]) - time;
       
      const numvideo = document.getElementById("num_video");
      var num_video = parseInt(numvideo.textContent)// Ajoute un zéro devant si nécessaire et prend les deux derniers chiffres
      
  
       $.ajax({
        url: "/create_interaction", // Remplacez '/your-endpoint-url' par l'URL de votre endpoint
        method: "GET",
        data: {
          start_time: start_time_update,
          end_time: stop_time_update,
          interaction: data["interaction"],
          selected_values: data["selectedValues"],
          commentaire: data["commentaire"],
          valide: data["valide"],
          num_video : num_video,
          dayHour: dayHour,
          camera: cameraSelect.value
        },
        success: function(response) {
            alert("Données envoyées avec succès");
            console.log("Réponse du serveur:", response);
            // Actualiser la page ou afficher un message de réussite, etc.
        },
        error: function(xhr, status, error) {
            alert("Échec de l'envoi des données");
            console.error("Erreur lors de l'envoi des données:", error);
            // Afficher un message d'erreur à l'utilisateur, etc.
        }
    });
  });
  }

  


  // Bouton affichage créer
  document
    .getElementById("afficherForm")
    .addEventListener("click", function () {
      var divForm = document.getElementById("monForm");
      if (divForm.style.display === "none") {
        divForm.style.display = "block";
      } else {
        divForm.style.display = "none";
      }
    });

  var urlVideoUsager = `static/video/json/${selectedCamera}_${dayHour}_user_light.json`;
  var urlVideoInteraction = `static/video/json/${selectedCamera}_${dayHour}.interaction.json`;

  // Charge les données JSON depuis le fichier
  $.getJSON(urlVideoUsager, function (data) {
    var ids = [];
    data.Data.forEach(function (obj) {
      ids.push(obj.ID); // Ajoute l'ID de chaque objet à la liste
    });

    // Ajoute les IDs à la liste déroulante
    var itemsList = document.querySelector(".items");
    ids.forEach(function (id) {
      var listItem = document.createElement("li");
      listItem.innerHTML =
        '<input type="checkbox" value="' +
        id +
        '" onclick="limitCheckboxSelection(this, 8)" />' +
        id;
      itemsList.appendChild(listItem);
    });
  });

  // Reste de votre code JS existant...
  // Si vous avez besoin d'ajouter d'autres fonctionnalités JavaScript, ajoutez-les ici.
  // Fonction pour charger la vidéo et les données JSON
  async function chargerVideoEtDonnees(camera, dayHour) {
    selectedCamera = camera;
    const videoUrl1 = `/video1?camera=${camera}&dayHour=${dayHour}`;
    const videoUrl2 = `/video2?camera=${camera}&dayHour=${dayHour}`;
    const dataUrl = `/data1?camera=${camera}&dayHour=${dayHour}`;
    const video = document.getElementById("video"); // Utilisez le même lecteur vidéo

    const url_usager1 = `/get_usagers1?camera=${camera}&dayHour=${dayHour}`;
    const url_interaction1 = `/get_interactions1?camera=${camera}&dayHour=${dayHour}`;

    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

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

    // Charger les données pour la première vidéo
    const data1 = await chargerDonneesJson(dataUrl);


    const data_usager1 = await chargerDonneesJson(url_usager1);
    const data_interaction1 = await chargerDonneesJson(url_interaction1);

    const urlminutesec = `/minutes_sec?camera=${camera}&dayHour=${dayHour}`;
    const data_minute_sec = await chargerDonneesJson(urlminutesec);

    if (data_usager1) {
      afficherUsagers(data_usager1);
      afficherID(data_usager1);
    }

    if (data_interaction1) {
      affichage_interaction_avec_data(data_interaction1, data_minute_sec);
    }

    video.src = videoUrl1;
    video.addEventListener("loadedmetadata", function () {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    });

    if (data1) {
      dessinerBoites(data1, video, ctx);
    }

    const day_hour = document.getElementById("day_hour");
    day_hour.textContent = startHour;

    const num_video = document.getElementById("num_video");
    num_video.textContent = 1;
    video.play();
    loaded();


    // Lorsque la première vidéo se termine, charger la deuxième vidéo et ses données
    var first_time = true;
    video.addEventListener("ended", async function () {
      if (first_time) {
        const data2Url = `/data2?camera=${camera}&dayHour=${dayHour}`;
      const data2 = await chargerDonneesJson(data2Url);

      loading();

      const url_usager2 = `/get_usagers1?camera=${camera}&dayHour=${dayHour}`;
      const data_usager2 = await chargerDonneesJson(url_usager2);

      if (data_usager2) {
        afficherUsagers(data_usager2);
        afficherID(data_usager2);
      }

      const url_interaction2 = `/get_interactions2?camera=${camera}&dayHour=${dayHour}`;
      const data_interaction2 = await chargerDonneesJson(url_interaction2);
      if (data_interaction2) {
        affichage_interaction_avec_data(data_interaction2, data_minute_sec);

      }

      video.src = videoUrl2;
      // Extraire l'heure de la deuxième vidéo du nom du fichier vidéo
      const dayHour_split = dayHour.split("_");
      const hour_from_filename = parseInt(dayHour_split[2]); // Extrayez l'heure du nom du fichier

      // Utiliser cette heure extraite comme startHour
      startHour = startHour + 1;
    
      const day_hour = document.getElementById("day_hour");
      day_hour.textContent = startHour;

      const num_video = document.getElementById("num_video");
      num_video.textContent = 2;

      if (data2) {
        dessinerBoites(data2, video, ctx);
      }
      video.play();
      loaded2();
      first_time = false;
      }
      

    });
  }

  function dessinerBoites(data, video, ctx) {
    // Variable pour stocker l'ID de la demande d'animation
    let animationId;

    // Créer un objet pour stocker les couleurs générées pour chaque ID
    const couleurs = {};

    // Fonction pour générer une couleur aléatoire pour un ID donné
    function genererCouleur(id) {
      // Vérifier si une couleur a déjà été générée pour cet ID
      if (couleurs[id]) {
        return couleurs[id];
      }
      // Générer une valeur aléatoire entre 0 et 255 pour chaque composante de la couleur
      const r = Math.floor(Math.random() * 256);
      const g = Math.floor(Math.random() * 256);
      const b = Math.floor(Math.random() * 256);
      // Créer une chaîne de couleur à partir des valeurs générées
      const couleur = `rgb(${r}, ${g}, ${b})`;
      // Stocker la couleur générée dans l'objet couleurs
      couleurs[id] = couleur;
      // Retourner la couleur générée
      return couleur;
    }

    // Fonction pour mettre à jour le canvas
    function updateCanvas() {
      // Effacer le canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Trouver les données correspondantes à la frame actuelle
      const currentTime = video.currentTime;
      const currentFrame = Math.floor(currentTime * 30);

      // Parcourir le tableau de données
      data.forEach((objet) => {
        if (objet.Usager == "car" || objet.Usager == "person" || objet.Usager == "bus" || objet.Usager == "bicycle" || objet.Usager == "truck") {
          // Parcourir le tableau de données de l'objet
          objet.data.forEach((obj) => {
            // Vérifier si l'ID de la frame correspond à la frame actuelle
            if (obj.frame_id === currentFrame) {
              // Générer une couleur aléatoire pour l'ID de l'objet
              const couleur = genererCouleur(objet.ID);

              // Dessiner la boîte autour de l'objet correspondant
              ctx.beginPath();
              ctx.rect(obj.x - obj.w / 2, obj.y - obj.h / 2, obj.w, obj.h); // Utiliser obj.x et obj.y directement
              ctx.lineWidth = 4;
              ctx.strokeStyle = couleur; // Utiliser la couleur générée
              ctx.stroke();

              // Dessiner le label avec la couleur générée
              ctx.fillStyle = couleur; // Utiliser la couleur générée
              ctx.font = "20px Arial";
              ctx.fillText(
                objet.Usager + " : " + objet.ID2,
                obj.x - obj.w / 2,
                obj.y - obj.h / 2 - 10
              ); // Utiliser obj.x et obj.y directement
            }
          });
        }
      });

      // Demander la prochaine mise à jour du canvas
      animationId = requestAnimationFrame(updateCanvas);
    }

    // Démarrer la mise à jour du canvas lorsque la vidéo est lue
    video.addEventListener("play", function () {
      updateCanvas();
    });
    // Arrêter la mise à jour du canvas lorsque la vidéo est mise en pause ou terminée
    video.addEventListener("pause", function () {
      cancelAnimationFrame(animationId);
      updateCanvas();
    });
    video.addEventListener("ended", function () {
      cancelAnimationFrame(animationId);
      updateCanvas();
    });
    // Mettre à jour le canvas lorsque la position de lecture de la vidéo est modifiée
    video.addEventListener("seeked", function () {
      cancelAnimationFrame(animationId);
      updateCanvas();
    });
  }

  // Écouteur d'événement pour changer de caméra
  const cameraSelect = document.getElementById("camera-select");
  cameraSelect.addEventListener("change", () => {
    const selectedCamera = cameraSelect.value;
    chargerVideoEtDonnees(selectedCamera, dayHour);
  });

  // Appel initial pour charger la vidéo et les données avec la première caméra sélectionnée
  // Appel initial pour charger la vidéo et les données avec la première caméra sélectionnée
  //chargerVideoEtDonnees(cameraSelect.value, dayHour);
  const video = document.getElementById("video");
  const timerElement = document.getElementById("timer");
  const timerTotal = document.getElementById("timer_totaleseconde");

  let timerInterval;
  let startHour = 0;

  function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours
      .toString()
      .padStart(
        2,
        "0"
      )}:${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }

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

  async function updateTimer(currentTime, camera, dayHour) {
    try {
      const timer = (currentTime - debut) * 1.42;
      const totalSeconds = (hour - 1) * 3600 + timer;
      const formattedTime = formatTime(totalSeconds);
      timerElement.textContent = `Temps écoulé : ${formattedTime}`;
      timerTotal.textContent = totalSeconds;
    } catch (error) {
      console.error("Erreur lors de la mise à jour du timer :", error);
    }
  }
  async function updateTimer_une_heure() {

    try {
      const timerTotal = document.getElementById("timer_totaleseconde");
      totalSeconds = parseInt(timerTotal.textContent,10)+3600;
      const formattedTime = formatTime(totalSeconds);
      timerElement.textContent = `Temps écoulé : ${formattedTime}`;
      timerTotal.textContent = totalSeconds;
      console.log("totalSeconds",totalSeconds);
    } catch (error) {
      console.error("Erreur lors de la mise à jour du timer :", error);
    }
  }
  video.addEventListener("play", () => {
    timerInterval = setInterval(() => {
      updateTimer(video.currentTime, selectedCamera, dayHour);
    }, 100);
  });

  video.addEventListener("pause", () => {
    clearInterval(timerInterval);
  });

  video.addEventListener("seeked", () => {
    updateTimer(video.currentTime, selectedCamera, dayHour);
  });

  video.addEventListener("timeupdate", () => {
    if (!video.paused && !video.seeking) {
      updateTimer(video.currentTime, selectedCamera, dayHour);
    }
  });

  const daysOfWeek = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
  ];
  const hours = [
    "00h-01h",
    "01h-02h",
    "02h-03h",
    "03h-04h",
    "04h-05h",
    "05h-06h",
    "06h-07h",
    "07h-08h",
    "08h-09h",
    "09h-10h",
    "10h-11h",
    "11h-12h",
    "12h-13h",
    "13h-14h",
    "14h-15h",
    "15h-16h",
    "16h-17h",
    "17h-18h",
    "18h-19h",
    "19h-20h",
    "20h-21h",
    "21h-22h",
    "22h-23h",
    "23h-00h",
  ];
  const dayMap = {
    Lundi: "2024_02_12",
    Mardi: "2024_02_13",
    Mercredi: "2024_02_14",
    Jeudi: "2024_02_15",
    Vendredi: "2024_02_16",
    Samedi: "2024_02_17",
    Dimanche: "2024_02_18",
  };
  const showCalendarButton = document.getElementById("showCalendar");
  const modal = document.getElementById("modal");
  const closeModal = document.getElementsByClassName("close")[0];
  const calendarContainer = document.getElementById("calendarContainer");

  showCalendarButton.addEventListener("click", function () {
    calendarContainer.innerHTML = ""; // clear previous content

    const cameraSelectDiv = document.createElement("div");
    cameraSelectDiv.innerHTML = `<h3>Caméra sélectionnée : ${selectedCamera}</h3>`;
    calendarContainer.appendChild(cameraSelectDiv);

    daysOfWeek.forEach((day) => {
      const dayDiv = document.createElement("div");
      dayDiv.classList.add("day");
      const dayHeader = document.createElement("h3");
      dayHeader.textContent = day;
      dayDiv.appendChild(dayHeader);
      console.log("starthour initiale : ", startHour);
      hours.forEach((hour) => {
        const hourButton = document.createElement("button");
        hourButton.textContent = hour;
        hourButton.addEventListener("click", function () {
          loading();

          const selectedDay = day;
          const selectedHour = hour;
          console.log("Jour:", selectedDay, "- Heure:", selectedHour);
          const day_actual_element = document.getElementById("day_actual");
          day_actual_element.textContent = dayMap[selectedDay].split("_")[2];

          const hourStart = parseInt(selectedHour.split("h")[0]);
          if (startHour == 0) {
            const hourStart = parseInt(selectedHour.split("h")[0]);
            startHour = hourStart; // Update start hour based on selected hour
            console.log("starthour : ", startHour);
          }

          dayHour = `${dayMap[selectedDay]}_${selectedHour.replace("h", "_")}`;
          console.log("DATEhOUR:", dayHour);
          chargerVideoEtDonnees(selectedCamera, dayHour);
        });
        hourButton.value = `${selectedCamera}_${dayMap[day]}_${hour.split("h")[0]
          }`;
        // Disable buttons initially
        hourButton.disabled = true;
        // Grey out buttons initially
        hourButton.style.backgroundColor = "grey";
        dayDiv.appendChild(hourButton);
      });

      calendarContainer.appendChild(dayDiv);
    });

    modal.style.display = "block"; // display the modal
    $.getJSON("/get_video_exist?camera=" + selectedCamera, function (response) {
      var videoFiles = response; // Les noms des fichiers vidéo seront stockés dans videoFiles
      // Activer les boutons pour les fichiers vidéo existants
      videoFiles.forEach(function (videoFile) {
        var button = document.querySelector(`button[value="${videoFile}"]`);
        if (button) {
          // Remove grey style
          button.style.backgroundColor = "";
          // Enable button
          button.disabled = false;
        }
      });
    });
  });

  closeModal.onclick = function () {
    modal.style.display = "none"; // hide the modal when close button is clicked
  };

  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none"; // hide the modal when clicked outside of it
    }
  };

  //   mise en place d'un temps de chargement pour attendre le chargement des données
  // il doit desctiver les bouton le temps du chargement et afficher un message de chargement avec un spinner
  // il doit les réactiver une fois les données chargées
  function loading() {
    console.log("loading");
    // créer un spinner au dessus de la page
    const spinner = document.getElementById("spinner");
    spinner.style.display = "block";
    load = false;
  }
  function loaded() {
    console.log("loaded");
    // cacher le spinner
    const spinner = document.getElementById("spinner");
    spinner.style.display = "none";

    // chargement du temps
    time_loading();
    load = true;
    console.log("load", load);

  }
  async function time_loading() {
    const camera = cameraSelect.value;
    const minutesSecUrl = `/minutes_sec?camera=${camera}&dayHour=${dayHour}`;
    const minutesSecData1 = await chargerDonneesJson(minutesSecUrl);

    if (minutesSecData1) {
      hour = dayHour.split("_")[dayHour.split("_").length - 1].replace("-", "").replace("h", "");
      debut =
        (3600 - minutesSecData1["minutes"] * 60 - minutesSecData1["seconds"]) *
        0.7;
      video.currentTime = debut;
      console.log("debut", debut);
      updateTimer(debut, selectedCamera, dayHour);
      init_data();
    }
  }
  function loaded2() {
    console.log("loaded...2");
    // cacher le spinner
    const spinner = document.getElementById("spinner");
    spinner.style.display = "none";

    // chargement du temps
    time_loading2();
    load = true;
    console.log("load...2", load);

  }
  async function time_loading2() {
    const camera = cameraSelect.value;
    const minutesSecUrl = `/minutes_sec?camera=${camera}&dayHour=${dayHour}`;
    const minutesSecData1 = await chargerDonneesJson(minutesSecUrl);

    if (minutesSecData1) {
      //hour = dayHour.split("_")[dayHour.split("_").length - 1].replace("-", "").replace("h", "");
      //debut =(3600 - minutesSecData1["minutes"] * 60 - minutesSecData1["seconds"]) *0.7;
      //video.currentTime = debut;
      //console.log("debut", debut);
      //updateTimer(debut, selectedCamera, dayHour);
      //updateTimer_une_heure();
      //hour = hour+1;
      console.log("hour :", hour);
      hour = parseInt(hour) + 1;

      console.log("hour+1 :", hour);
      init_data();
    }
  }
  // crée moi le spinner
  function spinner() {
    const spinner = document.createElement("div");
    spinner.id = "spinner";
    spinner.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); z-index: 9999;"></div>
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: white; padding: 20px; z-index: 10000;">
                <i class="fa fa-spinner fa-spin"></i>
                <p>Merci d'attendre...</p>
            </div>
        `;
    spinner.style.display = "none";
    document.body.appendChild(spinner);
  }
});