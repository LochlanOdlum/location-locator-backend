import * as cdk from 'aws-cdk-lib';
import { StackProps, Duration, RemovalPolicy } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as path from 'path';

export class CdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const repo = new ecr.Repository(this, 'LocatorRepo', {
      repositoryName: 'locator-backend',
    });

    // VPC with public and private subnets
    const vpc = new ec2.Vpc(this, 'LocatorVPC', {
      maxAzs: 2,
      natGateways: 0,
      subnetConfiguration: [
        {
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        },
      ],
    });

    const cluster = new ecs.Cluster(this, 'LocatorCluster', { vpc });

    // Create DB credentials in Secrets Manager
    const dbCredentialsSecret = new secretsmanager.Secret(
      this,
      'LocatorDBCredentialsSecret',
      {
        secretName: 'LocatorPostgresCredentials',
        generateSecretString: {
          secretStringTemplate: JSON.stringify({ username: 'postgres' }),
          excludePunctuation: true,
          includeSpace: false,
          generateStringKey: 'password',
        },
      }
    );

    // Create RDS instance
    const db = new rds.DatabaseInstance(this, 'LocatorPostgres', {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_15,
      }),
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      credentials: rds.Credentials.fromSecret(dbCredentialsSecret),
      allocatedStorage: 20,
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.T4G,
        ec2.InstanceSize.MICRO
      ),
      multiAz: false,
      publiclyAccessible: false,
      backupRetention: Duration.days(0),
      removalPolicy: RemovalPolicy.DESTROY, // Change for prod
      deletionProtection: false,
      storageEncrypted: true,
      databaseName: 'appdb',
    });

    // Allow ECS tasks to connect to RDS
    const dbSecurityGroup = db.connections.securityGroups[0];
    dbSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(5432),
      'Allow DB access'
    );

    const taskDef = new ecs.FargateTaskDefinition(this, 'LocatorTaskDef', {
      memoryLimitMiB: 512,
      cpu: 256,
    });

    // Read Cloudflare info from SSM
    const cfZoneId = ssm.StringParameter.valueForStringParameter(
      this,
      '/cloudflare/zone_id'
    );
    const cfRecordId = ssm.StringParameter.valueForStringParameter(
      this,
      '/cloudflare/record_id'
    );
    const cfApiToken = ssm.StringParameter.valueForStringParameter(
      this,
      '/cloudflare/api_token'
    );
    const hashSecret = ssm.StringParameter.valueForStringParameter(
      this,
      '/hash_secret'
    );
    const openRouteServiceAPIKey = ssm.StringParameter.valueForStringParameter(
      this,
      '/open_route_service_key'
    );

    const container = taskDef.addContainer('LocatorContainer', {
      image: ecs.ContainerImage.fromAsset(
        path.resolve(__dirname, '../../backend')
      ),
      logging: ecs.LogDriver.awsLogs({ streamPrefix: 'AppLogs' }),
      environment: {
        CF_ZONE_ID: cfZoneId,
        CF_RECORD_ID: cfRecordId,
        CF_API_TOKEN: cfApiToken,
        DB_HOST: db.dbInstanceEndpointAddress,
        DB_PORT: db.dbInstanceEndpointPort,
        AUTH_HASH_SECRET_KEY: hashSecret,
        OPENROUTESERVICE_API_KEY: openRouteServiceAPIKey,
        DB_NAME: 'appdb',
        DB_USER: 'postgres',
        STAGE: 'PROD',
      },
      secrets: {
        DB_PASSWORD: ecs.Secret.fromSecretsManager(
          dbCredentialsSecret,
          'password'
        ),
      },
    });

    container.addPortMappings({ containerPort: 80 });

    const service = new ecs.FargateService(this, 'LocatorService', {
      cluster,
      taskDefinition: taskDef,
      assignPublicIp: true,
      desiredCount: 1,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
    });

    service.connections.allowFromAnyIpv4(
      ec2.Port.tcp(80),
      'Allow public HTTP access on port 80'
    );
  }
}
