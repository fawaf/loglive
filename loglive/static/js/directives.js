'use strict';

angular.module('logliveDirectives', []).
directive('scrollToIf', function(){
    return function(scope, element, attributes){
        setTimeout(function(){
            if(scope.$eval(attributes.scrollToIf)){
                console.log(element[0]);
                console.log(element[0].offsetTop);
                console.log(window.innerHeight);
                window.scrollTo(0, element[0].offsetTop + 999);
            }
        });
    };
});
