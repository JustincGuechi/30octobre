$(document).ready(function() {
    // Chargement du JSON
    $.getJSON('/get_usagers', function(data) {
        // Création des options du menu déroulant
        var usagers = {};
        data.forEach(function(obj) {
            if (!usagers[obj.Usager]) {
                usagers[obj.Usager] = true;
                $('#usagerSelect').append('<option value="' + obj.Usager + '">' + obj.Usager + '</option>');
            }
        });

        // Écouteur d'événement pour le changement de sélection dans le menu déroulant
        $('#usagerSelect').change(function() {
            var selectedUsager = $(this).val();
            var html = '<h2>Détails de l\'usager sélectionné</h2>';
            html += '<ul>';
            data.forEach(function(obj) {
                if (obj.Usager === selectedUsager) {
                    html += '<li>ID: ' + obj.ID + '</li>';
                    html += '<li>Date et Heure: ' + obj.Datetime + '</li>';
                    html += '<li>Temps de début: ' + obj.Time_code_debut + '</li>';
                    html += '<li>Temps de fin: ' + obj.Time_code_fin + '</li>';
                }
            });
            html += '</ul>';
            $('#usagerDetails').html(html);
        });
    });
});
