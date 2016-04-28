# plugin.sh - DevStack plugin.sh dispatch script ceilometer_ecs

function install_ceilometer_ecs {
    cd $CEILOMETER_ECS_DIR
    sudo python setup.py install
}

function init_ceilometer_ecs {
    echo
}

function configure_ceilometer_ecs {
    iniset $CEILOMETER_CONF ecs endpoint $CEILOMETER_ECS_ENDPOINT
    iniset $CEILOMETER_CONF ecs use_floating_ip $CEILOMETER_ECS_USE_FLOATING_IP
    iniset $CEILOMETER_CONF ecs management_network $CEILOMETER_ECS_MANAGEMENT_NETWORK
}

# check for service enabled
if is_service_enabled ceilometer-ecs; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring system services for ECS Ceilometer"
        #install_package cowsay

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing ECS Ceilometer"
        install_ceilometer_ecs

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring ECS ceilometer"
        configure_ceilometer_ecs

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the ceilometer-ecs service
        echo_summary "Initializing ECS Ceilometer"
        init_ceilometer_ecs
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down ceilometer_ecs services
        # no-op
        :
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi
