function ShowSuccess($mdToast, msg) {
    $mdToast.show(
        $mdToast.simple()
            .textContent(msg || 'Changes Successfully Saved')
            .position('center top')
            .hideDelay(1000),
    );
}

function ShowError($mdDialog, error) {
    $mdDialog.show(
        $mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .title('Error Saving Fields')
            .textContent('Error: ' + error)
            .ariaLabel('Alert Dialog Demo')
            .ok('Close'),
    );
}

export {
    ShowSuccess,
    ShowError,
};
