/*********************************************
 * OPL 22.1.2.0 Model
 * Author: danhagen
 * Creation Date: Nov 20, 2025 at 12:49:28 PM
 *********************************************/

 
int N=...;

int K=...;
int D=7;

range Nr =1..N;
range Kr= 1..K;
range Dr=1..D;

int P[k in Kr] = ...;
int R[k in Kr] = ...;
int A[k in Kr] = ...;
int C[k in Kr] = ...;
 
int  M[i in Nr,j in Nr]=...;


dvar boolean KN[n in Nr, k in Kr];    /* kamera k installed at crossing n */
dvar boolean DKN[n in Nr, k in Kr, d in Dr];  /*  camera k active at crossing n at day d*/
/*dvar boolean ND[n in Nr, d in Dr];         /* crossing n coverd at day d*/

dexpr int totalCost =
/* price of camera * installed cameras  +   price per operaration * camera on days */
   sum(n in Nr, k in Kr) P[k] * KN[n,k] + sum(d in Dr, n in Nr, k in Kr) C[k] * DKN[n,k,d];


minimize totalCost;

    
subject to{
  
  
/* max 1 camera at a crossing */
forall(n in Nr)
  sum(k in Kr) KN[n,k] <= 1;



/* camera can only be on when installed*/
forall(n in Nr, d in Dr, k in Kr)
  	DKN[n,k,d]<= KN[n,k];
  
  

/* at least coverd by one each crossing */
forall(n in Nr, d in Dr)
  	sum( m in Nr , k in Kr: R[k] >= M[m,n])  DKN[m,k,d] >= 1;   /* all models of k that are large enough to cover m from n(n includes m) ,
  															check if at least on is on at m or n */


/* at least 2 days (prev or next 1 if on at day d)*/
forall(n in Nr, k in Kr, d in Dr)
  	DKN[n,k,d]<= DKN[n,k,(d==1) ? D : d-1 ] + DKN[n,k,(d==D) ? 1 : d+1 ];


/* for all days take go from that day to Ak days +1 further and check if the sum is <= Ak 
if its not means the days where all on , so consecutive and also larger then Ak so not allowed 
if d = 1  we check days 1 - 1+AK (with mod 7) we need to do  1+ (d + -1) bc mod goes to 0 and not 1 eg. :

t= 6 ofs =1 
mod7(6+1)= 0 (we want 7 tho)

So we do 
1+ mod7(6+1-1)=1+ mod7(6) = 1+6 = 7 */

forall(n in Nr, k in Kr, d in Dr)  
  sum(s in 0..A[k]) DKN[n,k , 1+ (d + s-1) mod 7]  <= A[k];  
  
}






