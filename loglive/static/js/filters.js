'use strict';

angular.module('logliveFilters', []).
filter('encodeUriComponent', function(){
    // this filter can't be named encodeURIComponent (with capital URI)
    // or else angular's dependency injection will look for
    // encodeURIComponentFilterProvider... in other words, it confuses the magic
    return function(input){
        return window.encodeURIComponent(input);
    };
}).
filter('monthNumberToText', function(){
    return function(input){
        var monthNumber = parseInt(input);
        switch(monthNumber){
            case 1: return "January";
            case 2: return "February";
            case 3: return "March";
            case 4: return "April";
            case 5: return "May";
            case 6: return "June";
            case 7: return "July";
            case 8: return "August";
            case 9: return "September";
            case 10: return "October";
            case 11: return "November";
            case 12: return "December";
        }
        return "Pandaberry";
    };
});

