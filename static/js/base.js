/**
 * Created by niebler on 06.03.17.
 */


$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 15 // Creates a dropdown of 15 years to control year
});

$(document).ready(function () {
    $('select').material_select();
});

