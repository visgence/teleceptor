import angular from 'angular';

function showSuccess($mdToast, msg) {

    $mdToast.show(
        $mdToast.simple()
            .textContent(msg || 'Changes Successfully Saved')
            .position('center top')
            .hideDelay(1000),
    );

}

function showError($mdDialog, error) {

    $mdDialog.show(
        $mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .title('Error')
            .textContent(error)
            .ariaLabel('Alert Dialog Demo')
            .ok('Close'),
    );

}

export {
    showSuccess,
    showError,
};
