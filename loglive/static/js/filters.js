'use strict';

angular.module('logliveFilters', []).
filter('encodeUriComponent', function(){
    // this filter can't be named encodeURIComponent (with capital URI)
    // or else angular's dependency injection will look for
    // encodeURIComponentFilterProvider... in other words, it confuses the magic
    return function(input){
        return window.encodeURIComponent(input);
    };
});

