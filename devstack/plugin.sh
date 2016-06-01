# plugin.sh - DevStack plugin.sh dispatch script ceilometer_ecs

function install_ceilometer_ecs {
    cd $CEILOMETER_ECS_DIR
    sudo python setup.py install
}

function init_ceilometer_ecs {
    echo
}

function configure_ceilometer_ecs {
    iniset $CEILOMETER_CONF ecs ecs_endpoint $CEILOMETER_ECS_ECS_ENDPOINT
    iniset $CEILOMETER_CONF ecs ecs_username $CEILOMETER_ECS_ECS_USERNAME
    iniset $CEILOMETER_CONF ecs ecs_password $CEILOMETER_ECS_ECS_PASSWORD
    iniset $CEILOMETER_CONF ecs ecs_cert_path $CEILOMETER_ECS_ECS_CERT_PATH
    iniset $CEILOMETER_CONF ecs sample_start_time $CEILOMETER_ECS_SAMPLE_START_TIME
    iniset $CEILOMETER_CONF ecs sample_interval $CEILOMETER_ECS_SAMPLE_INTERVAL
    iniset $CEILOMETER_CONF ecs sample_delay $CEILOMETER_ECS_SAMPLE_DELAY
    iniset $CEILOMETER_CONF ecs ceilometer_endpoint $CEILOMETER_ECS_CEILOMETER_ENDPOINT
    iniset $CEILOMETER_CONF ecs os_project_name $CEILOMETER_ECS_OS_PROJECT_NAME
    iniset $CEILOMETER_CONF ecs os_project_domain_name $CEILOMETER_ECS_OS_PROJECT_DOMAIN_NAME
    iniset $CEILOMETER_CONF ecs os_username $CEILOMETER_ECS_OS_USERNAME
    iniset $CEILOMETER_CONF ecs os_password $CEILOMETER_ECS_OS_PASSWORD
    iniset $CEILOMETER_CONF ecs os_user_domain_name $CEILOMETER_ECS_OS_USER_DOMAIN_NAME
    iniset $CEILOMETER_CONF ecs os_auth_url $CEILOMETER_ECS_OS_AUTH_URL
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
