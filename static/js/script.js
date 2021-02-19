  // Materialize CSS plugin jQuery initialisation script
  // Adapted from CI Task Manager mini project
  
  $(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
    $('.collapsible').collapsible();
    $('select').formSelect();
    $('input#input_text, textarea#textarea2').characterCounter();
  });
