#ifndef FCM_IO_H
#define FCM_IO_H 1

#include "icd.h"

typedef struct
{
    int instrStatus; //0-stop, 1-run, 2-pause; also used for handshake
    int handshake;

	CONTROLIN controlin;
	ATMOSIN atmosin;
	TERRAININ terrainin;

} MODELINPUT;

typedef struct
{
    int fcmStatus; //0-stop, 1-run, 2-pause; also used for handshake
    int handshake;

	BODYMOTION bodymotion;
	POWER power;
	INSTRUMENTDISP instrumentdisp;
	CONTROLDEFLECT controldeflect;
	ROTOR rotor;
    MISCOUT miscout; //for trim settings return	and simtime

} MODELOUTPUT;

#endif /* FCM_IO_H */
