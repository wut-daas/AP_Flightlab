#ifndef ARCHER_H_INCLUDED
#define ARCHER_H_INCLUDED 1

#define ARCHER_ICD_VERSION "1.0.0"


//INITIAL CONDITIONS-------------------------------------------------------------------------------
typedef struct  /* Aircraft initial conditions (rw) */
{
    double posxic;
    double posyic;
    double poszic;
    double speedic;
    double psiic;

    double climbrate;   /* [ft/sec]  added by MZ for trimming purposes */
    double turnrate;    /* [rad/sec] added by MZ for trimming purposes */
} AIRCRAFTIC;


//MODEL INPUTS-------------------------------------------------------------------------------------
typedef struct  /* Pilot inputs (input) */
{
    double xbtot;
    double xatot;
    double xctot;
    double xptot;
    double direct;
} CONTROLIN;
#define CONTROLIN_MAGIC (0xCB3E)


typedef struct  /* Atmospheric initial conditions (input) */
{
    double pressl;
    double tempsl;
    double windx;
    double windy;
    double windz;
} ATMOSIN;
#define ATMOSIN_MAGIC (0x6FE0)


typedef struct  /* Ground/Terrain information (input) */
{
    double tposx;
    double tposy;
    double tposz;
    double tnormx;
    double tnormy;
    double tnormz;
} TERRAININ;
#define TERRAININ_MAGIC (0x79B9)


//MODEL OUTPUTS------------------------------------------------------------------------------------
typedef struct  /* Equations of motion (output) */
{
    double posxi;
    double posyi;
    double poszi;
    double phi;
    double theta;
    double psi;
    double vxi;
    double vyi;
    double vzi;
    double vxb;
    double vyb;
    double vzb;
    double vxbd;
    double vybd;
    double vzbd;
    double phid;
    double thetad;
    double psid;
    double p;
    double q;
    double r;
    double pd;
    double qd;
    double rd;
} BODYMOTION;
#define BODYMOTION_MAGIC (0xB74F)


typedef struct  /* Equations of motion (output) */
{
    double rpm1;
    double rpm2;
    double shprtr1;
    double shprtr2;
    double shptotal;
} POWER;
#define POWER_MAGIC (0x8D92)


typedef struct  /* Instrument display (output) */
{
    double qdyn;
    double pamb;
    double oat;
    double tas;
    double ias;
    double iasx;
    double beta;
    double alpha;
    double vgrnd;
    double vclimb;
    double altagl;
    double hp;
} INSTRUMENTDISP;
#define INSTRUMENTDISP_MAGIC (0x5530)


typedef struct  /* Control deflections (output) */
{
    double theta1;
    double theta2;
    double b1s1;
    double a1s1;
} CONTROLDEFLECT;
#define CONTROLDEFLECT_MAGIC (0x8C69)


typedef struct  /* Main rotor (output) */
{
    double omega1;
    double beta01;
    double betac1;
    double betas1;
} ROTOR;
#define ROTOR_MAGIC (0x5B34)


typedef struct  /* Miscallenous outbuts by mzasuwa (output) */
{
    double xbtot;       /* Longitudinal cyclic (0%:forward; 100%:aft) [%] */
    double xatot;       /* Lateral cyclic (0%:left; 100%:right) [%] */
    double xctot;       /* Collective position (0%:down; 100%:up) [%] */
    double xptot;       /* Pedal position (0%:left; 100%:right) [%] */
    double simtime;     /* Simulation time [sec] */
} MISCOUT;
#define MISCOUT_MAGIC (0xB09F)


#endif /* ARCHER_H_INCLUDED */
