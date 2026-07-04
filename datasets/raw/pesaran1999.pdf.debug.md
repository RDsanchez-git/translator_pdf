Bounds Testing Approaches to the Analysis of Long
Run Relationships®

M. Hashem Pesaran
Trinity College, Cambridge

Yongcheol Shin
Department of Economics, University of Edinburgh

Richard J. Smith
Department of Economics, University of Bristol

February 1999

Abstract

This paper develops a new approach to the problem of testing the existence of a long-run
level relationship between a dependent variable and a set of regressors, when it is not known
with certainty whether the underlying regressors are trend- or first-difference stationary. The
proposed tests are based on standard F- and t- statistics used to test the significance of the
lagged levels of the variables in a first-difference regression. The asymptotic distributions of
these statistics are non-standard under the null hypothesis that there exists no level relation-
ship between the dependent variable and the included regressors, irrespective of whether the
regressors are 1(0) or 1(1). Two sets of asymptotic critical values are provided: One set as-
suming that all the regressors are I(1), and another set assuming that they are all 71(0). These
two sets of critical values provide a band covering all possible classifications of the regressors
into 1(0), I(1) or mutually cointegrated. Accordingly, various bounds testing procedures are
proposed. It is shown that the proposed tests are consistent, and their asymptotic distribution
under the null and suitably defined local alternatives are derived. The empirical relevance of
the bounds procedures are demonstrated by a re-examination of the earnings equation included
in the UK Treasury macroeconometric model. This is a particularly relevant application as
there is considerable doubt concerning the order of integration of the variables such as the
unemployment rate, the union strength and the wedge between the “real product wage” and

the “real consumption wage” that enter the earnings equation.

JEL Classification: C12, €22, C32.
Key Words: Long-Run Relationship, Unrestricted Error Correction Model, Cointegration, Unit Roots,
Bounds Tests, Critical Value Bounds, Asymptotic Local Power, Earnings Equation.

*We are grateful to Michael Binder, Clive Granger, Brian Henry, Joon-Yong Park and Ron Smith for

helpful comments. Partial financial support from the ESRC (grant No. R000233608) and the Isaac Newton
Trust of Trinity College, Cambridge, is gratefully acknowledged.


1 Introduction

Over the past decade considerable attention has been paid in empirical economics to testing
for the existence of long-run relations, mainly using cointegration techniques. There have
been two main approaches: the two-step residual-based procedure for testing the null of
no-cointegration (see Engle and Granger (1987), and Phillips and Ouliaris (1990)), and the
system-based reduced rank regression approach due to Johansen (1991,1995). There are also
other procedures such as the variable addition approach of Park (1990), the residual-based
procedure for testing the null of cointegration by Shin (1994), and the stochastic common
trends (system) approach of Stock and Watson (1988).

All these testing procedures require the underlying variables to be integrated of order 1;
or I(1). This inevitably involves a certain degree of pre-testing, thus introducing a further
degree of uncertainty into the analysis of long-run relations. (See, for example, Cavanagh et
al. (1995)).

In this paper we propose a new approach to testing for the existence of a long-run
relationship which is applicable irrespective of whether the underlying regressors are 1(0),
I(1) or mutually cointegrated. The statistic underlying our procedure is the familiar Wald or
F-statistic in a generalized Dicky-Fuller type regression used to test the significance of lagged
levels of the variables under consideration in an unrestricted error correction regression. We
show that the asymptotic distributions of both statistics are non-standard under the null
hypothesis that there exists no relationship between the levels of the included variables;
irrespective of whether the regressors are I(0), /(1) or mutually cointegrated. We establish
that the proposed test is consistent, and derive its asymptotic distribution under the null
and suitably defined local alternatives, again for a mixture of 1(0)/I(1) set of regressors.

We provide two sets of asymptotic critical values for the two polar cases: one which
assumes that all the regressors are I(1), and the other assuming that they are I(0). Since
these two sets of critical values provide critical value bounds for all classifications of the
regressors into /(1) and/or I(0), we propose a bounds testing procedure. If the computed
Wald or F-statistic falls outside the critical value bounds, a conclusive inference can be drawn
without needing to know whether the underlying regressors are /(1), cointegrated amongst
themselves or individually /(0). However, if the Wald or F-statistic falls inside the critical
values’ band, inference would be inconclusive and knowledge of the order of the integration
of the underlying variables will be needed before conclusive inferences can be made. We
also apply the bounds procedure to the cointegration test proposed in Banerjee, Dolado and
Mestre (1998) which is based on the t-ratio of the coefficient of the lagged dependent variable
in an augmented autoregressive distributed lag (ARDL) model. We derive the asymptotic
distribution of this t-statistic both in the case where all the regressors are I(1), the case
considered by these authors; and when one or more of the regressors are individually 1(0),
or are mutually cointegrated. We provide the relevant critical value bounds for this t-test as
well.

The empirical relevance of the bounds procedure is demonstrated by a re-examination
of the earnings equation included in the UK Treasury macroeconometric model. This is
a particularly relevant application as there is considerable doubt concerning the order of
integration of the variables such as the degree of unionization of the work force, the replace-

[1]


ment ratio (unemployment benefit-wage ratio) and the wedge between the “real product
wage” and the “real consumption wage” that typically enter the earnings equation. There
is another consideration in the choice of this application. Under the influence of the sem-
inal contributions of Phillips (1958) and Sargan (1964) econometric analysis of wages and
earnings has played an important role in the development of time series econometrics in the
UK. The work of Sargan is particularly noteworthy as it is one of the first to articulate and
apply the error correction mechanism to wage rate determination. Sargan, however, did not
consider the problem of testing the existence of a long-run relationship between real wages
and its determinants (which he considered to be the unemployment rate, the index of labour
productivity in manufacturing, the ratio of consumption expenditures at market prices to
consumption expenditures at factor costs, and a linear time trend).

The long-run levelrelationship underlying Treasury’s earning equation relates real average
earnings of the private sector to labour productivity, the unemployment rate, an index of
union density, a wage variable (comprising a tax wedge and an import price wedge) and
the replacement ratio (defined as the ratio of the unemployment benefit to the wage rate).
These are the variables predicted by the bargaining theory of wage determination reviewed,
for example, in Layard, Nickell and Jackman (1991). We estimated a number of ARDL
models in these five variables and found that once a sufficiently high order is selected for the
conditional model, the hypothesis that there exists no long-run level relationship between
these variables is rejected; irrespective of whether they are I(0) or I(1). Having established
the existence of a long-run level relationship between these variables, we then use the ARDL
modelling approach advanced in Pesaran and Shin (1999) to estimate our preferred error
correction model of average earnings. In our analysis the identification problem discussed by
Manning (1993) is approached by assuming that the level of the unemployment rate enters
the wage equation, but not vice versa. This assumption, of course, does not preclude the rate
of change of earnings entering the unemployment equation, or there being other long-run
level relationships between the remaining four variables. Our approach accommodates both
possibilities.

The plan of the paper is as follows: Section 2 sets out the underlying model and addresses
the issues involved in testing for the existence of long-run level relationships. Section 3
considers the Wald statistic (or the F-statistic) for testing the hypothesis that there exists no
long-run level relation between the variables under consideration and derives the associated
asymptotic theory. Section 4 discusses the power properties of the proposed test. Section 5
describes the empirical application. Section 6 provides some concluding remarks.

The following notations will be used. The symbol = signifies “weak convergence in
probability measure,” I,, “an identity matrix of order m,” I(d) “integrated of order d,”
Op(K) “of the same order as K in probability” and op(K) “of smaller order than K in
probability”.


2 The Underlying VAR Model and Assumptions

Let {z,}°, denote a (k + 1)-vector random process. The data generating process for {z;}:°,
is the vector autoregressive model of order p (VAR(p)):

where L is the lag operator, pu and 4 are unknown (k + 1)-vectors of intercepts and trend
coefficients, the (k + 1,k + 1) matrix lag polynomial ®(L) = I — > 0 | &, L* with {®;}) |
(k 4+ 1,k + 1) matrices of unknown coefficients. The properties of the (k + 1)-vector error
process {&€:}7°, are given in Assumption 2 below. All the analysis of this paper is conducted
given the initial observations Zo = (z1_y, ..., Zo). We make the following assumptions.

Assumption 1. The roots of |I; 1 — Zle @izi] = ( are either outside the unit circle |z| = 1
or satisfy z = 1.

Assumption 2. The vector error process {&:};°; is IN(0,Q), Q positive definite.

Assumption 1 permits the elements of z; to be I(1), I(0) or cointegrated but excludes
the possibility of seasonal unit roots and explosive roots.! Assumption 2 may be relaxed
somewhat to permit {€;}7°, to be a conditionally mean zero and homoskedastic process; see,
for example, Pesaran, Shin and Smith (1998, Assumption 4.1).

We may re-express the lag polynomial ®(L) in vector error correction form; wviz.

®(L) = ~L+T(L)(1 - L). (2.2)

In (2.2), the long-run multiplier matrix is defined by

= — (Im — Z c1>i> (2.3)

and the short-run response matrix lag polynomial I'(L) = I,,,— f:_ll AT, = — Z?:Hl D,
i=1,...,p— 1. Hence, the VAR(p) model (2.1) may be rewritten in vector error correction
form as
p—1
AZt = ao—l—alt—I—Hzt_l +ZPiAZt—i+€t7 = 1,2,..., (24)
=1
where A = 1 — L is the difference operator,

ao=—Ip+ (T+1)y, a, = -1, (2.5)

and the sum of the short-run coefficient matrices

—1
=1 =1

! Assumptions 5a and 5b below further restrict the maximal order of integration of {z;}3°; to unity.

[3]


As detailed in Pesaran, Shin and Smith (1998, Section 2), if ¥ # 0, the restrictions (2.5)
on the trend coefficients a; in (2.4) ensure that the deterministic trending behaviour of the
level process {z;}$°; is invariant to the (cointegrating) rank of II; a similar result holds for
the intercept of {z,;};°, if 4 # 0 and v = 0.

The interest of this paper concerns the conditional modelling of the scalar process
given the k-vector x; and the past values {zt_i}z;i and Zg, where we have partitioned
z; = (y¢, X;)". Partitioning the error term €, conformably with z; = (y},X}) as &, = (£, €0,)’

_ [ Wy Wy

we may express £,, conditionally in terms of €, as

and its variance matrix as

where u; ~ IN(0,wyu), Wuy = wyy — wme;mlwmy and u; is independent of €,;. Substitution
of (2.7) into (2.4) together with a similar partitioning of the parameter vectors and matrices

provides a conditional model for Ay; in terms of z;_{, Ax;, Az;_1,Az;_o, ...; viz.
p—1
7 7
Ay =co+ et +my .21 + E YAz + W AR + Uy, (2.8)
i=1
— — -1 — ! — ’ [ /
[ 1,2,..., where w = Qmwmy, Co = Qyo — Wagp, C1 = Qy1 — W ay, '()bz = ")/yz- — wl—‘m-,

i=1,..,p—1, and 7, , = w, — W'II,. The deterministic relations (2.5) are modified to

where v, , =7, —w'T,.
We now partition the long-run multiplier matrix II conformably with z, = (y}, x})" as

T T
0= vy ve )
< Ty Hmm
The next assumption is critical for the analysis of this paper.

Assumption 3. The k-vector m,, = 0.

Under Assumption 3,

p—1
Axy = a0 + apit + X1 + Z IpiAzy_; + €44, (2.10)
i=1
t =1,2,.... Therefore, we may regard the process {x;}7°, as long-run forcing for {y;}°, as

there is no feedback from the level of ; in (2.10); see Granger and Lin (1995).? Assumption

ZNote that this restriction does not preclude {y;}32; being Granger-causal for {x;}?°; in the short-run.

[4]


3 ensures that there exists al most one long-run level relationship between 7, and x; which
includes both y; and x;, irrespective of the level of integration of the process {x;}°,; see
(2.13) below.

Under Assumption 3, the conditional error correction model (2.8) now becomes

p—1
Ayt = Cp + Clt + ﬂ_yyyt—l + Tfym.mxt_l + Z '(p;-AZt_,,; + w,AXt + U, (211)
=1
t=1,2,..., where
co = —(Tyy, Tyaa) b + ['Yy.z + (Tyys Tyaa) Y, €1 = —(Tyy, Tya)Y (2.12)

and Ty, = Ty — WI,,2

The next assumption together with Assumptions 5a and 5b below which constrain the
maximal order of integration of the system (2.11) and (2.10) to be unity defines the cointe-
gration properties of the system.

Assumption 4. The matrix II,, has rank r, 0 <r < k.

Therefore, under Assumption 4, from (2.10), we may express II,, as
I, = O‘mm/B,mma

where o, and 3,, are both (k,r) matrices of full column rank; see, for example, Engle
and Granger (1987) and Johansen (1991). If the maximal order of integration of the system
(2.11) and (2.10) is unity, under Assumptions 1, 3 and 4, the process {x;}:°, is mutually
cointegrated of order 7, 0 < r < k. However, in contradistinction to, for example, Banerjee
et al. (1998) who fix » = 0, we do not wish to impose an a priori specification of 7. When
Ty = 0 and II,,; = 0, then x; is weakly exogenous for the coefficients 7, and 7y, , = Ty,
in (2.11); see, for example, Johansen (1995, Theorem 8.1, p.122). Moreover, in the more
general case where Il;, is non-zero, as m,, and T, , = Ty, — W', are variation-free from
the parameters in (2.10), x; is also weakly exogenous for the parameters of (2.11).

Note that under Assumption 4 the maximal cointegrating rank of the long-run multiplier
matrix II for the system (2.11) and (2.10) is 7 + 1 and the minimal cointegrating rank of
IT is 7. The next assumptions provide the conditions for the maximal order of integration
of the system (2.11) and (2.10) to be unity. Firstly, we consider the requisite conditions for
the case in which rank(II) = r. In this case, under Assumptions 1, 3 and 4, 7, = 0 and
Ty — @'l = 0 for some k-vector ¢p. Note that 7, , = 0' implies the latter condition.
Thus, under Assumptions 1, 3 and 4, the long-run multiplier matrix Il has rank r and is

(0 my,

3Pesaran, Shin and Smith (1998) and Harbo et al. (1998) consider a similar model but where x; are 7(1);
that is, under the additional assumption II,, = O.

given by


Hence, we may express II = a3’ where a and 3 are (k + 1,7) matrices of full column rank

Qyy B o
o= (ar)e=(4.)

Let the columns of the (k 4+ 1,k — 7 4+ 1) matrices (aj, a'’) and ( j,,@L), where aqj, ,qu
and o, B are respectively (k 4+ 1)-vectors and (k 4+ 1,k — r) matrices, denote bases for
the orthogonal complements of respectively a and 3; in particular, (aj, a’t)a = 0 and

(8,.87)B=0.

and

Assumption 5a. If rank(Il) = r, the matrix (c, aL)T(,Bj,,BL) is full rank k —r + 1,
0<r<k.

Cf. Johansen (1991, Theorem 4.1, p.1559).

Secondly, if the long-run multiplier matrix II has rank r + 1, then under Assumptions 1,
3 and 4, 7, # 0 and II may be expressed as II = a, 3, + af’, where a, = (ay,,0') and
B, = (Byy B;m)’ are (k + 1)-vectors, the former of which preserves Assumption 3. For this
case, the columns of a and B form respective bases for the orthogonal complements of

(ay, @) and (B,,B); in particular, a''(a,, a) =0 and I@M(/@yﬂ@) —0
Assumption 5b. If rank(IT) = r + 1, the matrix a'T8" is full rank k —r, 0 <r < k.

Assumptions 1, 3, 4 and 5a and 5b permit the two polar cases for the {x;}$°; process. Firstly,
if {x;}7°, is an I(0) vector process, then II,,, and, hence, o, and 3,,, are nonsingular.
Secondly, if {x;}3°, is an I(1) vector process, then II,, = 0, and, hence, a,, and 3,, are
also null matrices.

Therefore, under Assumptions 1, 3, 4 and 5b, it immediately follows from (2.11) that, if
Tyy 7 0 and 7y, , # 0, there exists a non-degenerate long-run level relationship between y,
and x; defined by

where 0y = —co/myy, 01 = —c1/7y, and 8 = —7,, /7, and {v;} is a zero mean stationary
process. Note that the long-run level relationship (2.13) between y; and x;, t = 1,2, ...,
may be degenerate in the sense that m,,, = 0" is possible as well as the non-degenerate
T2z 7 0'. The former possibility is somewhat of an anomaly from an applied perspective
as the differenced variable Ay, then depends on its own lagged level y;_; in the ECM (2.11)
but not on the lagged levels x;_; of the forcing variables, t = 1,2, .... In this case there are
no long-run effects running from x; to y; and the long-run relationship of the model only
involves 1, and possibly a deterministic trend, t = 1,2, ....

In order to test for the absence of a long-run level relationship between 7; and x;, the
method adopted in this paper is to examine the joinl hypothesis 7, = 0 and 7wy, = 0 in

4Using (A.1) in Appendix A it is easily seen that (m,,, 7y, )2 = (Tyy, Ty o) (p+~t+ C*(L)e;). Hence,


the ECM (2.11).° In contradistinction, the approach of Banerjee et al. (1998) may be simply
described in terms of (2.11) using Assumption 5b:

Ay = co+ et + ayy(Byye + Bgﬂxt—l) + (Qye — W' Qga) Bl X1
p—1

=1

Banerjee et al. (1998) test for the exclusion of y;—1 in (2.14) when r = 0, that is, 3,, = 0
in (2.14) or II,; = 0 in (2.10) and, thus, {x;} ~ I(1); cf. Harbo et al. (1998) and Pesaran,
Shin and Smith (1998). Effectively, therefore, Banerjee et al. (1998) consider the hypothesis
oy, = 0 (or Hy" : m, = 0).° More generally though, when 0 < r < k, we require the
imposition of the subsidiary hypothesis oy, — w'a,, = 0'; that is, the limiting distribution
of the Banerjee et al. (1998) test is obtained under the joint hypothesis 7, = 0 and 7w, » = 0,
in (2.11).

In the following sections of the paper, we focus on (2.11) and differentiate between five
cases of interest delineated according to the specification of the deterministics; viz.

e Case I: (No Intercepts; No Trends.) ¢p = 0 and ¢; = 0. That is, g = 0 and v = 0.
Hence, the ECM (2.11) becomes

p—1

=1

e Case II: (Restricted Intercepts; No Trends.) c¢op = —(myy, Tyzo)pt and ¢; = 0. Here,
v = 0. The ECM is

p—1
Ay, = 7Tyy<yt—1 — fiy) + ﬂ-ym.m<xt—1 — ) + Z '(,b;'AZt—i + W AX; + uy,
=1 (2.16)

where p = (uy, i)' is partitioned conformably with z, = (y;, x})".

e Case III: (Unrestricted Intercepts; No Trends.) ¢ # 0 and ¢; = 0. Again, v = 0.
In this case, the intercept restriction c¢o = —(my,, Tyz.)p is ignored and the ECM
estimated is

p—1

=1

5This joint hypothesis may also be justified by the application of Roy’s union-intersection principle to
tests of 7y, =0 in (2.11) given . .. Let W,  (7ys..) be the Wald statistic for testing m,, = 0 for a given
value of ;.. The test maxy,  Wr, (7y...) is identical to the Wald test of m,, = 0 and wy,, = 0 in
(2.11).

SPartitioning I'y; = (Yey.i»Tzz,i), t = 1,...,p — 1, conformably with z; = (y;,x;)’, Banerjee et al. (1998)
also set v,,; = 0,7 = 1,...,p — 1, which implies v,, = 0, where I'; = (v,,,Ts:); that is, Ay; does not
Granger cause AX;.

[7]


e Case I'V: (Unrestricted Intercepts; Restricted Trends.) ¢ # 0 and ¢1 = — (7, Tyaa)Y-
Thus

p—1
Aye = co+ Ty (Y1 — Wh) + Tpea(Xeo1 = Yot) + > YAz + W' Axy + uy,
i1 (2.18)

where v = (1, 7,)" 1s partitioned conformably with z, = (v, x})".

e Case V: (Unrestricted Intercepts; Unrestricted Trends.) ¢ # 0 and ¢; # 0. Here, the

deterministic trend restriction ¢; = —(7yy, Tz )7 1s ignored and the ECM estimated
is
p—1
Ay = co + 1t + TyyYe—1 + TyzaXe—1 + Z YAz + W AX + Uy
i—1 (2.19)

It should be emphasised that the DGPs for Cases II and III are treated as identical as
are those for Cases IV and V. However, as in the test for a unit root proposed by Dickey
and Fuller (1979) compared with that of Dickey and Fuller (1981) for univariate models,
estimation and hypothesis testing in Cases IIl and V proceed ignoring the constraints linking
respectively the intercept and trend coeflicient vectors, ¢y and ¢, to the parameter vector
(Tyy, T ya.o) Whereas Cases II and IV fully incorporate the restrictions in (2.12).

In the following exposition, we concentrate on Case IV, that is, (2.18), which may be
specialised to yield the remainder.

3 Bounds Tests for a Long-Run Level Relationship

In this section we develop bounds procedures for testing for the existence of a long-run level
relationship between the levels of y, and x;, t = 1,2, ..., using (2.15)-(2.19); see (2.13). The
approach taken here, cf. Engle and Granger (1987) and Banerjee et al. (1998), is to test for
the absence of any long-run relationship between the levels of y; and x;, ¢ = 1,2, ...; that is,
the exclusion of the lagged level variables y;—1 and x;_; in (2.15)-(2.19). Consequently, we
define the constituent null hypotheses

Hy® iy =0, Hy "™ i Wy = 0
and alternative hypotheses
H™ oy 0, H™ g0 £ 0.
Hence, the joint null hypothesis of interest in (2.15)-(2.19) is given by:
Hy = Hy* N Hy ™" (3.1)
and the alternative hypothesis is correspondingly stated as:

Hy = H" U HJv=. (3.2)

8]


As indicated in Section 2, not only does the alternative hypothesis H; of (3.2) cover the case
of interest in which 7, , # 0’ but also permits 7, , = 0’; ¢f. (2.11). That is, the possibility
of a degenerate long-run relationship between the levels of y; and x;, t = 1,2, ..., is admitted
under [ of (3.2).

For ease of exposition, we again consider Case IV and rewrite model (2.18) in matrix
notation as

Ay =trco + 27, + AZ_% +u, (3.3)

where ¢ is a T-vector of ones, Ay = (Ayy,...,Ayr), AX = (Axy,...,Axy), AZ_; =
22 = (tr, Z-1), Tr=(1,..,T), Z_1 = (20, ..., 2Zr-1), u = (uy, ..., ur) and

s _ (Y Tyy

The least squares (LS) estimator of T, . 18 given by:

1_ _ o~

Y.

where Zil =PZ",, AZ_ = P,AZ._, A\Sr = P, Ay, P, = Iy — tp(tper) e, and f’fz, =
7

1
I —AZ_ AZI_AZ_) AZ_. The Wald and the F-statistics for testing the null hypothesis
Hy of (3.1) against the alternative hypothesis I of (3.2) are respectively:

W= 20 Py R 0w F = g, (3.5)

where

1 T

B = T_mZaf, (3.6)
=1

m=(k+1)(p+1)+1 is the number of estimated coeflicients and @, t = 1,2,..., T, are the

least squares (LS) residuals from (3.3).

The next theorem presents the asymptotic null distribution of the Wald statistic; the limit
behaviour of the F-statistic is a simple corollary and is not presented here or subsequently.
Let W;y_,11(a) = (Wy(a), Wi_.(a)') denote a (kK — r + 1)-dimensional standard Brownian
motion partitioned into the scalar and (k — r)-dimensional sub-vector independent standard
Brownian motions W,(a) and Wy_.(a), a € [0,1]. We will also require the corresponding

de-meaned (k: — 74+ 1)—vector standard Brownian motion

Wk_7-+1<a) = Wi_r1(a) —/0 Wi_ri1(a)da, (3.7)

and de-meaned and de-trended (m — T)—vector standard Brownian motion
. _ 1 1 1\ -
Wk_7.+1<a) = Wk—r+l (a) —12(a— 5 a — 5 Wk—r+l (a)da, (38)
0

[9]


and their respective partitioned counterparts Wk_7-+1 (a) = ( Wu(a), Wi;_.(a)"), and Wk_7-+1<a) =

(Wu(a), Wi_(a)"), a € [0,1].
Theorem 3.1 (Limiting Distribution of W.) If Assumptions 1-4 and 5a hold, then under
Ho : myy =0 and wy,, = 0 of (3.1), as T — oo, the asymptotic distribution of the Wald
statistic W of (3.5) has the representation

-1

/ P (@)dWa(a).

W =zz + /01 dW,(a)Fr_ry1(a) </01 F’f—’"“(a)Fk_Hl(a)lda> (3.9)

where z, ~ N(0,1,) is distributed independently of the second term in (8.9) and

Wi_ri1(a) Case I
(Wi—ri1(a)', 1) Case 11
Fi_,i1(a) = _ Wi_ri1(a) Case 111
(Wk_lurl(a)’, a—3) Case IV
Wi _,11(a) Case V

r=0,...,k, and Cases I-V are defined in (2.15)-(2.19), a € [0,1].

The asymptotic distribution of the Wald statistic W of (3.5) depends on the dimension
and cointegration rank of the forcing variables {x;}, k¥ and r respectively. In Case IV,
referring to (2.14), the first component in (3.9), z.z, ~ x*(r), corresponds to testing for
the exclusion of the r-dimensional stationary vector 3,,x; 1, that is, the hypothesis o, —
w'a,, = 0') whereas the second term in (3.9), which is a non-standard Dickey-Fuller unit-
root distribution, corresponds to testing for the exclusion of the (k —r 4 1)-dimensional (1)
vector (,qu,,@'L)'zt_l and, in Cases II and IV, the intercept and time-trend respectively or,
equivalently, o, = 0.

We specialise Theorem 3.1 to the two polar cases in which, firstly, the process for the
forcing variables {x;} is integrated of order zero, that is, 7 = k and I1,, is of full rank, and,
secondly, the {x;} process is not mutually cointegrated, 7 = 0, and, hence, the {x;} process
is integrated of order one.

Corollary 3.1 (Limiting Distribution of W if {x;} ~ 1(0).) If Assumptions 1-4 and 5a
hold and r = k, that is, {x;} ~ 1(0), then under Hy : my, = 0 and Typp = 0 of (3.1), as
T — oo, the asymptotic distribution of the Wald statistic W of (3.5) has the representation

(Jo Fla)iW.(a))
(fol F(a)2da) 7

where zy ~ N(0,1;) is distributed independently of the second term in (5.10) and

W = z,z; + (3.10)

W, (a) Case I
(Wau(a), 1) Case II
F(a) = - Wa(a) Case IIT }
(Wu(a),a - 3) Case IV
W, (a) Case V

r=0,...,k, where Cases I-V are defined in (2.15)-(2.19), a € [0, 1].

[10]


Corollary 3.2 (Limiting Distribution of W if {x;} ~ I(1).) If Assumptions 1-4 and 5a
hold and r = 0, that is, {x:} ~ I(1), then under Hy : my, = 0 and Typp = 0 of (3.1), as
T — oo, the asymptotic distribution of the Wald statistic W of (3.5) has the representation

1 1 -1
0 0 0
where Fy1(a) is defined in Theorem 3.1 for Cases I-V, a € [0, 1].

See also Boswijk (1992).

In practice, however, it is unlikely that one would possess a priori knowledge of the rank
r of Il,,; that is, the cointegration rank of the forcing variables {x;} or, more particularly,
whether {x;} ~ I(0) or {x;} ~ I(1). Long-run analysis of (2.15)-(2.19) predicated on a prior
determination of the cointegration rank 7 in (2.10) is prone to the possibility of a pre-test
specification error; see, for example, Cavanagh et al. (1995). However, it may be shown
by simulation that the asymptotic critical values obtained from Corollaries 3.1 (r = k and
{x¢} ~ 1(0)) and 3.2 (r = 0 and {x;} ~ I(1)) provide lower and upper bounds respectively
for those corresponding to the general case considered in Theorem 3.1 when the cointegration
rank of the forcing variables {x;} process is 0 < r < k.” Hence, these two sets of critical
values provide critical value bounds covering all possible classifications of {x;} into 1(0),
I(1) and mutually cointegrated processes. Therefore, Tables C1.i-Cl.v provide two sets of
asymptotic critical values for the F-statistics covering Cases I-V; one set assuming that the
forcing variables {x;} are I(0) and the other assuming that {x;} are /(1).®

Hence, we suggest a bounds procedure to test Hy : my,, = 0 and m,,, = 0" of (3.1),
that is, the absence of a long-run level relationship between 1, and x;, within the ECMs
(2.15)-(2.19). If the computed Wald or F'- statistics fall outside the critical value bounds,
a conclusive decision results without needing to know the cointegration rank r of the {x;}
process. If, however, the Wald or F- statistic fall within these bounds, inference would be
inconclusive. In such circumstances, knowledge of the cointegration rank r of the forcing
variables {x,} is required to proceed further.

The ECM (2.15)-(2.19), derived from the underlying VAR(p) model (2.4), may also be
interpreted as an autoregressive distributed lag model of orders (p, p, ...,p) (ARDL(p, ..., p)).
However, one could also allow for differential lag lengths on the lagged variables y;_; and x;_;
in (2.4) to arrive at, for example, an ARDL(p, q1, g2, ..., &) without affecting the asymptotic
results derived in this section. Hence, our approach is quite general in the sense that one
can use a flexible choice for the dynamic lag structure in (2.15)-(2.19) as well as allowing for
short-run feedbacks from the lagged dependent variables, Ay,_;, i =1, ..., p, to Ax, in (2.10).
Moreover, within the single equation context, the above analysis is more general than the
cointegration analysis of partial systems carried out by Boswijk (1992, 1995), Harbo et al.
(1998), Johansen (1992, 1995), Pesaran, Shin and Smith (1998) and Urbain (1992), where it
is assumed in addition that IT,, = 0 or {x;} ~ I(1) in (2.10).

"The critical values of the Wald and F- statistics in the general case (not reported here) may be computed
via stochastic simulations with different combinations of values for & and 0 <r < k.

8The critical values for the Wald version of the bounds test are given by % + 1 times the critical values of
the F-test in Cases I, III and V, and k + 2 times in cases II and IV .

[11]


To conclude this section, we re-consider the approach of Banerjee et al. (1998). There are
three scenarios for the deterministics given by (2.15), (2.17) and (2.19) respectively. Note
that the restrictions on the deterministics’ coefficients (2.12) are ignored in Cases II and IV
and, thus, Cases Il and IV are now subsumed by Cases I1I and V respectively. To summarise,
the three cases considered are

e Case I: (No Intercepts; No Trends.) ¢p = 0 and ¢; = 0. The ECM estimated is

p—1

=1

e Case III: (Unrestricted Intercepts; No Trends.) ¢o # 0 and ¢; = 0. The ECM
estimated is
p—1

=1

e Case V: (Unrestricted Intercepts; Unrestricted Trends.) ¢o # 0 and ¢; # 0. The
ECM estimated is
p—1
Ay, = co+ cil + TyyYi1 + TyzaXe—1 + Z ’l/J;AZt—i + W AX; + uy,
=1 (3.13)

As noted below (2.14), the implicit hypothesis oy, — W', = 0' is also imposed but not
tested; that is, the limiting distributional results given below are also obtained under the
joint hypothesis Hy : 7y, = 0 and 7y, = 0" of (3.1). Banerjee et al. (1998) test a,, = 0
(or Hy* : m,, = 0) via the exclusion of y,_; in Cases I, IIT and V; that is, (3.11), (3.12) and
(3.13). For example, in Case V, they consider the ¢-statistic

where @,, is defined in (3.6), &Sf =P, AY, Y 1 =Py, Y1 = (W0, yro1), X_g =

]-SLT,TTX—L X—l = (X(), ceey XT_l),, AZ_ = ].SLT’TTAZ_, ].SLT’TT = ].SLT—].SLTTT<T,T].3LTTT>_ITIT].3LT,
Py x =Pxy Pry X (X Pg X)X Py, andPg, =1,-AZ (AZ_AZ )'AZ..

Theorem 3.2 (Limiting Distribution of the t-statistic for Hy" : m,, = 0.) If Assumptions
1-4 and 5a hold and ~y,, = 0, where I';, = ('mea Ly.), then under Hy : 7y = 0 and my, , =0’
of (8.1), as T — 00, the asymplotic distribution of the t-stalistic for Hy*" : m,, = 0 has the
representation

—1/2

/0 W () Py (a) < /0 1 Fk_,,<a)2da> | (3.14a)

[12]


where

-1
W(a) — fol W, (a)Wy_.(a)da (fl Wi (a)W a) Wi_.(a) Casel
(a) = fy W) Wi (a)da (
(a) = fy Wa(a)Wi_(a)da (

r =0,...k, and Cases I, III and V are defined in (3.11), (3.12) and (3.13) respectively,
a € [0,1].

k—r(a)d
Jo Wi (@)Wir(a)da) " Wi_,(a) Case TII
fol Wi (a)Wy_, (a)’da)

Fk—7”<a’) = VNVu -
~ -1
Wy(a) — Wi_.(a) CaseV

The form of the asymptotic representation (3.14a) is similar to that of a Dickey-Fuller test
for a unit root except that the standard Brownian motion W, (a) is replaced by the residual
from an asymptotic regression of W, (a) on the independent (k—1)-vector standard Brownian
motion Wy_,(a) (or their de-meaned and de-meaned and de-trended counterparts). As is
emphasised in the Proof of Theorem 3.2 given in Appendix A, if the asymptotic analysis
is conducted under Hy* : m,, = 0 only, the resultant limit distribution depends on the
nuisance parameter w — ¢, where, under Assumption 5a, o, — ¢ o, = 0'. Moreover, if Ay,
is allowed to Granger-cause Axy, that is, 7,,; # 0 for some i = 1,...,p — 1, then the limit
distribution also is dependent on the nuisance parameter v, / (Vyy — ¢l7zy)3 see Appendix
A.

Similarly, to the analysis following Theorem 3.1, we detail the limiting distribution of the
t-statistic for m,, = 0 in the two polar cases in which the forcing variables {x;} are integrated
of order zero and one respectively.

Corollary 3.3 (Limiting Distribution of the t-statistic for Hy" : m,, = 0 if {x;} ~ 1(0).)
If Assumptions 1-4 and 5a hold and r = k, that is, {x;} ~ 1(0), then under Hy : my, = 0 and
Tyee =0 0f (3.1), as T — oo, the asymptotic distribution of the t-statistic for Hy*" : m,, =0

has the representation
—1/2

/01 dW ,(a)F(a) </01 F(a)2da> ,

W,(a) Case I
F(a) ={ W,(a) Case III
W,(a) Case V

and Cases I, 111 and V are defined in (3.11), (3.12) and (5.13) respectively, a € [0,1].

where

J

Corollary 3.4 (Limiting Distribution of the t-statistic for Hy* : my, = 0 if {x:} ~ I(1).)
If Assumptions 1-4 and 5a hold and r = 0, that is, {x:} ~ I(1), then under Hy : m,, = 0 and
Tyee =0 0f (3.1), as T — oo, the asymptotic distribution of the t-statistic for Hy*" : m,, =0

has the representation
1 1 —-1/2
/ dW,(a)Fx(a) </ Fk(a)2da> ,
0 0

[13]


where

W, (a) — fl W, (a)Wy(a)da (fo Wk(a)Wk(a)’da)_l Wi(a) Casel

Fi(a) =< Wy(a) - fol W (a)Wy(a)da (fol Wk(a)wk(a)’da)_l Wy(a) Case IIT ;,
W.(a) — fol W.(a)Wy(a)da (fol Wk(a)wk(a)’da) Wy(a) Case V

and Cases I, 111 and V are defined in (3.11), (3.12) and (5.13) respectively, a € [0,1].

As above, it may be shown by simulation that the asymptotic critical values obtained from
Corollaries 3.3 (r = k and {x;} ~ I(0)) and 3.4 (r = 0 and {x;} ~ I(1)) provide lower and
upper bounds respectively for those corresponding to the general case considered in Theorem
3.2. Hence, a bounds procedure for testing Hy" : m,, = 0 based on these two polar cases
may be implemented as described above based on the t-statistic for the exclusion of ;_1 in
the ECMs (3.11), (3.12) and (3.13) without prior knowledge of the cointegrating rank r; see
Tables C2.i, C2.iii and C2.v for Cases I, III and V respectively.

4 The Asymptotic Power of the Bounds Procedure

This section firstly demonstrates that the proposed bounds testing procedure described in
Section 3 is consistent. Secondly, it derives the asymptotic distribution of the Wald statistic
under a sequence of local alternatives.

In the discussion of the consistency of the bounds test procedure, because the rank of
the long-run multiplier matrix II may be either r or 7 + 1 under the alternative hypothesis
Hy = H{* U H7*** of (3.2) where H{* : m,, # 0 and H{ """ : w,,, # 0, it is necessary
to deal with these two possibilities. Firstly, under H{*" : m,, # 0, the rank of Il is 7 + 1 so
Assumption 5b applies; in particular, oy, # 0. Secondly, under Hy* : m,, = 0, the rank of
II is r so Assumption 5a applies; in this case, H; """ : Wy, # 0’ holds and, in particular,
Oy — W, # 0.

Theorem 4.1 (Consistency of the Bounds Test Procedure under H{*.) If Assumptions 1-
and 5b hold, then under H{*" : m,, # 0 of (3.2) the Wald statistic W (5.5) is consistent
against H{" : m,, # 0 in Cases I-V defined in (2.15)-(2.19).

Theorem 4.2 (Consistency of the Bounds Test Procedure under Hy *** N Hy*".) If Assump-
tions 1-4 and 5a hold, then under Hy """ : wyp. # 0 of (3.2) and Hy* : m, = 0 of (3.1)
the Wald statistic W (5.5) is consistent against Hy*** : Tyz. # 0" in Cases I-V defined in
(2.15)-(2.19).

Hence, combining Theorems 4.1 and 4.2, the bounds procedure of section 3 based on
the Wald statistic W (3.5) defines a consistent test of Hy = Hy* N Hy*"" of (3.1) against
Hy = H{* U H{*"" of (3.2). This result holds irrespective of whether the forcing variables
{x¢} are 1(0), I (1) or mutually cointegrated.

[14]


We now turn to consider the asymptotic distribution of the Wald statistic (3.5) under a
suitably specified sequence of local alternatives. Recall that under Assumption 5b

Tyz[= (Tyy, Tyaa)] = (QyyByy, O‘yy/@‘;y + (e — W' aze) B,,)-
Consequently, we define the sequence of local alternatives

Hyr 2wy or[= (Tyyr, Tyear)] = (T_layyﬂyya T_layy/@‘;y + T_1/2<5ym — W' 802)B)-

(4.1)
Hence, under Assumption 3, defining
TyyT TyaT
L. = Y y
and recalling IT = a3', where (1, —w')a = oy, — w'az, = 0, we have
Oy — I =T""'o, B, + T~/ < gym > g (4.2)

In order to detail the limit distribution of the Wald statistic under the sequence of local
alternatives Hyp of (4.1), it is necessary to define the (kK — r + 1)-dimensional Ornstein-
Uhlenbeck process J;_,,;(a) = (J;(a),J;_.(a)")" which obeys the stochastic integral and
differential equations

Jis (@) = Weera(a) + abl / Ti o (r)dr
0

and

dI;_,11(a) = dWi_ria(a) +ab' I}, (a)da,

where Wy_,;1(a) is a (k — r 4+ 1)-dimensional standard Brownian motion and

a=[(oy, ") Q ey, )] (e, ) ey,

b =[(,, ) Qe )] (8, 87) ey, . )] (B,. ) B,
together with the de-meaned and de-meaned and de-trended counterparts j,*;_r 11la) =
(j;(a),jz_r(a)’)’ and j,*;_rﬂ(a) = (j;(a),jz_r(a)’)’ partitioned similarly, a € [0,1]. See,
for example, Johansen (1995, Chapter 14, pp.201-210).

Theorem 4.3 (Limiting Distribution of W under Hyp.) If Assumptions 1-4 and 5a hold,
then under Hyp = my 5 = T‘lozyy,@';—l-T_lﬁ(éym—w’(sm),@" of (4.1), asT — oo, the asymptotic
distribution of the Wald statistic W of (3.5) has the representation

1

W =zz + /0 dJ* (a)Fy_ i1 (a)’ < /0 1 Fk_m(a)Fk_TH(a)’da) B /0 le_r+1(a)dJZ<a<>LLS>

[15]


where 7, ~ N(Q'n.1,), Q= QUQ?) = plimy. . (T78.2" P, ,8.). 1= (6,0 -
Ww'd,,), is distributed independently of the second term in (4.3) and

Jr . (a) Case I
GL @)1y Case Tt
Fi_ri1(a) = _ Jisa(a) Case IIT }
(Jiri1(a)a - ) Case IV
Jr . 1(a) Case V

r=0,...,k, and Cases I-V are defined in (2.15)-(2.19), a € [0,1].

The first component of (4.3) z.z, is non-central chi-square distributed with r degrees
of freedom and non-centrality parameter 'Qn and corresponds to the local alternative
HIE" : Wypar = T_1/2((5ym — W'8yy)3,, under Hy* : m,, = 0. The second term in (4.3)
is a non-standard Dickey-Fuller unit-root distribution under the local alternative H ¥ :
Ty = T ay,B,, and §,, — w'd,, = 0. Note that under Hy of (3.1), that is, a,, = 0 and
dyr — w0, = 0, the limiting representation (4.3) reduces to (3.9) as should be expected.

5 An Application: UK Earnings Equation

In this section we provide a re-examination of the earnings equation included in the UK
Treasury macroeconometric model described in Chan, Savage and Whittaker (1995, CSW).
The theoretical basis of Treasury’s earnings equation is the bargaining model advanced in
Nickell and Andrews (1983) and reviewed, for example, in Layard, Nickell and Jackman
(1991, Chapter 2). The theoretical derivation of the earnings equation is based on a Nash
bargaining framework where the firms and the unions set wages to maximize a weighted
average of the firm’s profits and the union’s utility. Following Darby and Wren-Lewis (1993),
the theoretical real wage equation underlying Treasury’s earnings equation is given by

B Prod;
- 14+ F(UR)(1—RRy)’

Uniong

(5.4)

Wy

where w; is the real wage, Prod, is labour productivity, RR, is the replacement ratio defined
as the ratio of unemployment benefit to the wage rate, Union, is a measure of “union power”,
and f(UR;) is the probability of a union member becoming unemployed, which is assumed
to be an increasing function of the unemployment rate, U R;. The econometric specification
is based on a log-linearized version of (5.4) after allowing for the wedge effect that takes
account of the difference between the “real product wage” which is the focus of the firm’s
decision, and the “real consumption wage” which is the focus of the union.® The theoretical
arguments for a possible long-run wedge effect on real wages is mixed and, as emphasized by
CSW, whether such long-run effects are present is an empirical matter. The change in the
unemployment rate (AUR;) is also included in the Treasury’s wage equation. CSW cite two

9The wedge effect is further decomposed into a tax wedge and an import price wedge in the Treasury
model, but this decomposition is not pursued here.

[16]


different theoretical rationale for the inclusion of AU R; in the wage equation: the differential
moderating effects of long-term and short-term unemployed on real wages, and the ‘insider-
outsider’ theories which argue that only rising unemployment will be effective in significantly
moderating wage demands. See Blanchard and Summers (1986) and Lindbeck and Snower
(1989). The ARDL model and its associated unrestricted error correction formulation that
we shall be using automatically allow for such effects.

Following the modelling approach proposed in this paper we start from the maintained
assumption that the time series properties of the key variables in Treasury’s earnings equa-
tion can be well approximated by a log-linear VAR(p) model, augmented with appropriate
deterministic components such as intercepts or time trends. To ensure comparability of our
results with those of the Treasury, the replacement ratio is not included in the analysis.
CSW (p. 50) report that “... it has not proved possible to identify a significant effect from
the replacement ratio, and this had to be omitted from our specification.” Also, as in CSW,
we include two dummy variables to take account of the effects of incomes policies on average
earnings. These dummy variables are defined by

D7475, = 1 during the 8 quarters of 1974-75 and zero elsewhere,
D7579; = 1 during the 20 quarters of 1975-79 and zero elsewhere.

The asymptotic theory developed in the paper is not affected by the inclusion of such “one-
off” dummy variables.!® Let

z, = (wq, Prod,, U R, Wedge,, Union,) = (w;,x})",

then using the analysis of Section 2 the conditional model of interest can be written as

p—1
i=1 (5.5)

Under the assumption that lagged real wages, w;_1, do not enter the sub-VAR model for x;,
the above real wage equation is identified and can be estimated consistently by the OLS.!!
Notice, however, that this assumption does not rule out the inclusion of lagged changes in
real wages in the unemployment or productivity equations, for example. The exclusion of the
level of real wages from the unemployment and productivity equations is an identification
requirement and allows us to identify the bargaining theory of wages from other alterna-
tives, such as the efficiency wage theory which postulates that labour productivity is partly

10The asymptotic theory and the associated critical values must, however, be modified in the case of the
dummy variables where the fraction of periods in which the dummy variables are non-zero does not tend to
zero with the sample size, T'.

1See Assumption 3 and the discussion that follows it. Notice that by construction the contemporaneous
effects, Ax;, are uncorrelated with the disturbance term, u;, and instrumental variable estimation which
has been particularly popular in the empirical literature on the wage equation is not needed. In fact, given
the unrestricted nature of the lag distribution of the conditional model, (5.5), it is difficult to find suitable
instruments: namely variables that are not already included in the model, which are uncorrelated with u;
and at the same time have a reasonable degree of correlation with the variables that are included in (5.5).

[17]


determined by the level of real wages.!? It is clear that the bargaining theory as set out in
CSW and the efficiency wage theory can not be entertained simultaneously, at least not in
the long run. Our framework does, of course, allow for changes in real wages to affect labour
productivity or the unemployment rate.

The above specification is also based on the assumption that the disturbances, u;, are
serially uncorrelated. It is therefore important that p, the order of the underlying VAR, is
selected appropriately. There is a delicate balance between choosing p to be sufficiently large
to mitigate the residual serial correlation problem, and at the same time sufficiently small
so that the model is not unduly over-parameterized, particularly in view of the limited time
series data which is available.

Finally, a decision must be made concerning the time trend in (5.5) and whether its
coefficient should be restricted.!® This issue can only be settled in light of the particular
sample period under consideration. The time series data we shall be using are quarterly,
cover the period 1970q1-1997q4, and are seasonally adjusted (when relevant).!* To ensure
comparability of the estimation results for different choices of p, we carried out all the
estimations over the period 1972q1-1997q4 (a total of 104 quarters), and reserved the first 8
observations for the construction of lagged variables.

The five variables in the earnings equation were constructed from primary sources in the

following manner:
w ) ERPR;
= n —
! PYNONG;)’

prog 1o (YPROM, +278.29 « Y MF,
rode = EME, + ENMF, ’
100 % ILOU,
UR, = In{———— "t
te <1L0Uf ¥ WFEMPT> ’
RPIX

Union; = In(UDEN),

where FRPR, is average private sector earnings per employee (£), PY NONG; is the
non-oil non-government GDP deflator, Y PROM, is output in the private, non-oil, non-
manufacturing, and public traded sectors at constant factor cost (£million,1990), Y M F} is
manufacturing output index adjusted for stock changes (1990=100), EM F; and EN M F} are
respectively employment in UK manufacturing and non-manufacturing sectors (thousands),
ILOU; is the International Labour Office (ILO) measure of unemployment (thousands),
WFEMP, is total employment (thousand), T'E}; is the average employers National Insur-
ance contribution rate, T'D, is the average direct tax rate on employment incomes, RPI X,
is the Retail Price Index excluding mortgage payments, and U D E N, is union density (used
to proxy union power) and measured as union membership as a percentage of employment.

2For a discussion of the issues that surround the identification of the wage equation see Manning (1993).

13See, for example, Pesaran, Shin and Smith (1998), and the discussion at the end of Section 2.

4We are grateful to Andrew Gurney and Rod Whittaker for providing us with the data. For further
details about the sources and the descriptions of the variables see Chan et al. (1995, pages 46-51, and page
11 of its Annex).

[18]


5.1 Empirical Results

The time series plots of real wages (average earnings) and the productivity variable clearly
show steadily rising trends with real wages growing at a slightly faster rate than productivity.
This suggests, at least initially, that the linear trend need to be included in the real wage
equation (5.5). Also the application of the unit root tests to the five variables, perhaps not
surprisingly, yields mixed results; with strong evidence in favour of the unit root hypothesis
only in the case of the real wage and the productivity variables. This does not, of course,
necessarily mean that the other three variables (UR, Wedge, and Union) are not likely
to have any long-run impacts on real wages. Following the methodology developed in this
paper it is possible to test the existence of a long-run real wage equation involving all the
five variables irrespective of whether they are 1(0), I(1), or mutually cointegrated.!®

To determine the appropriate lag length, p, and whether a deterministic linear trend is
also required in addition to the productivity variable, we estimated the conditional model
(5.5) by the OLS with and without a linear time trend, for p = 1,2,...,7. As pointed out
earlier all the regressions were computed over the same period, 1972q1-1997q4. We found
that lagged changes of the productivity variable, A Prod;_1, AProd;_s,..., were not significant
(either singly or jointly) in any of the regressions. Therefore, for the sake of parsimony and to
avold unnecessary over-parameterization we decided to re-estimate the regressions without
these lagged variables, but including the lagged changes of all the other variables. Table 1
gives the Akaike’s Information and Schwarz’s Bayesian Criteria, denoted respectively by AIC
and SBC, and the Lagrange multiplier (LM) statistics for testing the hypothesis of residual
serial correlation of order 1 and 4. These are denoted by x%.(1) and x%.(4), respectively.

As to be expected the lag order selected by the AIC, namely p,;. = 6 irrespective of
whether a deterministic trend term included in the model or not, is much larger than the
lag order selected by the SBC. This latter criterion estimates p to be only 1 when the
model contains a trend and 4 when it does not. The Y%, statistics also suggest using a
relatively high lag order: 4 or more. In view of the importance of the assumption of serially
uncorrelated errors for the validity of the bounds test, it seems prudent to select p to be
either 5 or 6.1 A higher lag order does not seem necessary. Nevertheless, in what follows
for completeness we report the test results for p = 4,5 and 6. The results in Table 1 also
show that there is little to choose between the conditional model with and without a linear
deterministic trend.

Table 2 gives the values of the F- and t-statistics for testing the existence of a long-
run earnings equation under 3 different cases depending on whether the model contains a
linear trend and whether the trend coefficients are restricted. See Sections 3 for a detailed
discussion of these cases.

5The view that long-run relationships could exist only among variables that are integrated of order 1 or
higher is implicit in much of the empirical literature on cointegration.

16Tn the Treasury model different lag orders are chosen for different variables. The highest lag order
selected is 4; applied to the log of the price deflator and the wedge variable. The estimation period of the
earnings equation in the Treasury model is 1971q1-1994q3.

19]


Table 1+
Statistics for Selecting the Lag Order of the Earnings Equation

With Deterministic Trends . Without Deterministic Trends

|p | AIC | SBO | xso(l) [ xso() | | AIC | SBO | xio(l) | xsc(d) |

1131053 502,14 [ 16,55 [85.50° | [ 31751 | S0L6L | 1535 [ 3159

2 [524.95 [ 30177 [ 216 [ 10717 | [32377 [ 30262 [ 105 [ 2152 |

5 (32051 [ 20874 [ 052 | 17.07 | [ 32057 | 0L43 | 156 [ 1935 |
T [330.57 [ 50131 [ 845 | 779" | | 3337 | 803.63 | 3417 [ 713 |
5 (3355020750 [0.03 [ 250 | 33600 29047 [ 008|215 |
6 (33706 [ 20542 [ 085|358 | [ 33703 | 0472000 [8.09 |
7 (336,96 | 25500 [0.07 220 | | 33655 250.25 [ 009|064 |

* Notes: p is the lag order of the conditional model (5.5), with zero restrictions on the coefficients of
lagged changes in the productivity variable. AIC, = LL, —s, and SBC, = LL, — %” In(T), are the Akaike

and Schwarz Information Criteria, where LL, is the maximized log-likelihood value of the model, p is the

lag order, s, is the number of freely estimated coefficients, and 7" is the sample size. x%.(1) and x%-(4) are
the LM statistics for testing residual serial correlations of orders 1 and 4. The symbols {, %, and ** represent

significance at 1% or less, 5% or less, and 10% or less, respectively.

Table 2-

F- and t- Statistics for Testing the Existence of a Long-Run Earnings Equation

With Without
p | Deterministic Trends | Deterministic Trends

I T A T 7 T

302
6475 350 oa 54| 3

* Notes: p is the lag order of the underlying model. See also the notes to Table 1. Fjy is the F-statistic for

testing zero restrictions on the coeflicients of the lagged level variables and the trend term in (5.5). Fy is
the F-statistic for testing zero restrictions on the coefficients of the lagged level variables in (5.5). Fjjs is the
F-statistic for testing zero restrictions on the coeflicients of the lagged level variables in (5.5) without the
trend term. ty and %777 are the t-ratios of the coefficient of w;_; in (5.5) with and without a deterministic
linear trend. a denotes that the statistic lies below the 95% lower bound, & denotes it falls within the 95%
bounds, and ¢ denotes that it falls outside the 95% upper bound.

[20]


The various statistics in Table 2 need to be compared with the critical value bounds
provided in Tables C1 and C2. First consider the bounds F test. For the model with a
deterministic trend, Fy is the standard F-statistic for testing the restrictions 7, = 0 and
Twer = 0, while Fpy, is the standard F-statistic for testing 7, = 0, Tz = 0, and ¢ = 0,
in (5.5). As has been argued in Pesaran, Shin and Smith (1998), the statistic Fy which
sets the trend coefficient to zero under the null of no level long-run relationship is more
appropriate than Iy which does not impose such a restriction. Notice that when the trend
coeflicients are not restricted, (5.5) implies a quadratic trend in real wages under the null
hypothesis of 7., = 0 and 7., = 0, which is not plausible. The critical value bounds for
the statistics Fjy and Fy are given in Tables Cl.iv and Cl.v, respectively. Since the model
contains 4 regressors, the 95% critical value bounds are (3.66, 4.76) and (3.47, 4.57) for Fy
and Iy, respectively. The test outcome critically depends on the choice of the lag order, p.
For p = 4 the hypothesis that there exists no long-run earnings equation is not rejected at
the 95% level, irrespective of whether the regressors are /(0) or I(1). For p =5 the bounds
test is inconclusive. For p = 6 (selected by the AIC) the statistic Fy- is still inconclusive,
but Fry = 4.78 just lies outside the 95% critical value bounds and rejects the null hypothesis
that there exists no long-run earnings equation, irrespective of whether the regressors are
I(0) or I(1).'” This conclusion is confirmed even more conclusively when the bounds F-test
is applied to the earnings equations without a linear trend. The relevant test statistic is
Fir1, and its associated 95% critical value bounds are (2.86, 4.01).18 For p =4, Fy;; = 3.63,
and the test result is inconclusive. But for p = 5 and 6 the values of Fy;; are 5.23 and 5.42
and the hypothesis of no long-run earnings equation is conclusively rejected.

The results from the application of the bounds t-tests to the earnings equations are less
clear cut and do not allow the imposition of the trend restrictions discussed above. The two
t-statistics reported in Table 2, ty, and t;77, are the t-ratios of the OLS estimate of 7, in
(5.5), with and without a linear time trend, respectively.!® The 95% critical value bounds
for t77; and ty tests are (-2.86, -3.99) and (-3.41, —4.36).20 Therefore, when a linear trend is
included in the model the bounds t-test does not reject the null hypothesis even for p = 5
or 6. But when the trend term is excluded the null hypothesis is just rejected for p = 5.

Overall, the test results support the existence of a long-run earnings equation when a
sufficiently high lag order is selected and when the statistically insignificant deterministic
trend term is excluded from the conditional model. Such a specification is in accord with
the evidence on the performance of the alternative conditional models set out in Table 1,
and in the remainder of this section we focus our attention on this specification and provide
estimates of the long-run coeflicients and the short-run dynamics based on a conditional
earnings equation with p = 6, but without a deterministic time trend. For this model, using
the ARDL approach to the estimation of the long-run relations discussed in Pesaran and
Shin (1999), we obtain the following level long-run earnings equation?!

"The same conclusion is also reached for p=7.

18See Table C1.iii.

Notice also that lagged changes in the productivity variable are excluded.

20See Tables C2.iii and C2.v, for & = 4 under the columns headed 95%.

2INotice that the ARDL approach advanced in Pesaran and Shin (1999) is applicable irrespective of
whether the regressors are 1(0) or I(1).

[21]


wy = 1.063 Prod; —0.114UR; —0.998Wedge, +1.495Union, +2.714 oy,
(0.0526) (0.0398) (0.0297) (0.377) (0.274) (5.6)

where 7y is the error-correction term. The standard errors of the long-run estimates are given
in brackets.?? All the long-run estimates are highly significant and have the expected signs.
The coefficients of the productivity and the wedge variables do not differ significantly from
unity. In Treasury’s earnings equation the long-run coeflicient of the productivity variable is
imposed to be unity, and the above estimates can be viewed as providing empirical support
for such an a priori restriction. Our long-run estimates of the effects of the unemployment
rate and the union variable on real wages (namely -0.114 and 1.495) are also in line with

1.%22 The main difference between the two sets of estimates

Treasury estimates of -.09 and 1.3
concerns the long-run coefficient of the wedge variable. We obtain a much larger estimate,
almost twice as much as the estimate obtained by the Treasury.

The error correction regression associated with the above (level) long-run relationship
is given in Table 3.2* These estimates provide further direct evidence on the complicated
dynamics that seem to exist between real wage movements and its main determinants.?
All the five lagged changes in real wages are statistically significant, further justifying the
choice of p = 6. The error correction coefficient is estimated to be —0.235 (0.0675),%% which
is reasonably large and highly significant. The auxiliary equation of the autoregressive part
of the model has the real roots 0.9258, and —0.8931, and two pairs of complex roots with
moduli, 0.7853, and 0.5951; thus suggesting an initially cyclical real wage process which
slowly converges towards its equilibrium given by (5.6).%” Despite the many insignificant
coefficients that are retained in this error correction specification, the regression fits rea-
sonably well and satisfies the diagnostic tests for non-normal errors and heteroskedasticity.
However, it fails the functional form misspecification at the 5% level; which may be sugges-
tive of some non-linear effects or asymmetries in the adjustment of real wage process that
our linear specification is incapable of taking into account.?® Recursive estimation of the

22The long-run estimates and their standard errors are computed using Microfit 4.0. See Pesaran and
Pesaran (1997).

23(CSW do not report standard errors for the long-run estimates of the Treasury earnings equation.

24Tn practice it may be desirable also to derive a more parsimonious error correction model by impos-
ing a unit long-run coefficient on the productivity variable and by dropping lagged changes with (jointly)
statistically insignificant coeflicients. But for our purposes this does not seem to be necessary.

2>The standard errors of the estimates reported in Table 3 allow for the uncertainty associated with the
estimation of the long-run coeflicients. This is important in the present application where it is not known
with certainty whether the regressors are I(0) or 7(1). Ounly in the case where it is not known for sure that
all the regressors are I(1) and cointegrated would it be reasonable in large samples to treat the estimates of
the long-run level coefficients as known; on the grounds of their super-consistency.

26The error correction coefficient in the Treasury’s earnings equation is estimated to be —0.1848 (0.0528),
which is quite a bit smaller than our estimate. (See p. 11 in Annex of CSW.) This seems to be due to the
shorter lag lengths used in the estimation of the Treasury’s equation rather than the fact that it has been
estimated over a shorter time period: 1971q1-1994¢3. Notice also that the t-ratio reported for this coefficient
does not have the standard t-distribution.

2"The complex roots are 0. 3406 4 0. 707 67, and —0.201 6 £ 0.585 9, where i = /—L.

2The error correction regression in Table 3 also passes the residual serial correlation test. However, the

[22]


error correction model also suggests that the regression coefficients are generally stable over
the sample period. The cumulative sum and cumulative sum of squares plots based on the
recursive residuals are given in Figures 1 and 2 and do not show evidence of statistically
significant breaks. However, these tests are known to have low powers and are likely to have
missed some important breaks. Overall, the error correction earnings equation presented in
Table 3 has a number of desirable features and provides a sound basis for further research.

model was chosen specifically to meet this test, and should not therefore be given any extra credits for
passing the serial correlation test!

[23]


Table 3

Error Correction Form of the Earnings FEquation
(Dependent variable: Awy, Estimation Period: 1972q1-1997q4)

N/
Awt—l
Ry 002
Awt—?:
Koy 07
Ruis 038
R Prod; 00
AUR, 599
AUR, P
AUR., 651
AUR, 02
AR 016
AUR,, 903
W edge,
AW edge,; 372
RV edger 101
AW edge,—s 05
W edger—s 366
AT edge,, S8
Almion, 46
Rl nion;_ 03
Al nion,— 508

R? = 5473, 6 =.0084, AIC =337.03, SBC =294.72,
Xzo(4) = 3.99[.408], x%p(1) =5.831.016], x%(2) = 0.82[.663], x%(1) = 0.22[.638]

* Notes: The error correction term, 9,1, is defined by (5.6). The regression is based on the conditional
model (5.5) with p = 6, but excluding lagged changes in the productivity variable. R? is the adjusted squared
multiple correlation coefficient, & is the standard error of the regression, AIC and SBC are the Akaike and
Schwarz Information Criteria, x%-(4), X%(1), X4 (2), and x% (1) are the Chi-squared statistics for tests
of residual serial correlation, functional form mis-specification, non-normal errors and hetroskedasticity,

respectively. For the details of these diagnostic tests see, for example, Pesaran and Pesaran (1997, Ch. 18).

[24]


Plot of Cumulative Sum of Recursive Residuals for the Earnings Equation
2
1
1

1

-2

-2
1972Q1 1974Q3 1977Q1 1979Q3 1982Q1 1984Q3 1987Q1 1989Q3 1992Q1 1994Q3 1997Q1

The straight lines represent critical bounds at 5% significance level

Figure 1

Plot of Cumulative Sum of Squares of Recursive Residuals - Earnigs Equation

/

00 | - - - m e e Tl

1.5

1.0

05

-0.5
1972Q1  1974Q3 1977Q1 1979Q3 1982Q1 1984Q3 1987Q1 1989Q3 1992Q1 1994Q3 1997Q1

The straight lines represent critical bounds at 5% significance level

Figure 2

[25]


6 Concluding Remarks

Empirical analysis of long run relationships has been an integral part of time series econo-
metrics and pre-dates the recent literature on unit roots and cointegration?® However, the
emphasis of this early literature was on the estimation of long-run relationships and did
not address the testing problem. The cointegration literature attempts to fill this vacuum,
but under the relatively restrictive assumption that the regressors, x;, entering the long-run
determination of the dependent variable of interest, 1, are all integrated of order 1 or more.
In this paper we show that the problem of testing the existence of a long-run relationship
between 7; and X; continues to be present and furthermore is non-standard even if all the
regressors under consideration are I(0). This is because under the null hypothesis that there
exists no long-run relationship between ¥, and X, the ¥y, process will be I(1), irrespective of
whether the regressors are 1(0), I(1) or mutually cointegrated. The asymptotic theory de-
veloped in this paper provides a framework for testing the existence of a single long-run level
relationship between ¥y, and x; when it is not known with certainty whether the regressors
are 1(0), I(1) or mutually cointegrated.®® In this framework it is not necessary for the order
of integration of the underlying regressors to be ascertained first, before the existence of a
long-run relationship between 1; and x; can be tested; and therefore unlike the cointegration
analysis is not subject to this particular pre-testing problem. The application of the proposed
bounds testing procedure to the UK earnings equation highlights this point, where one need
not take a position as to whether the rate of unemployment or the union density variable,
for example, are (1) or 1(0). It is, however, worth emphasizing that the test developed
in this paper is not appropriate in situations where there may be more than one long-run
level relationship involving ;. Extending our approach to deal with such cases is relatively
straightforward, but involves further theoretical developments and requires computation of
new critical values.

29For an excellent review of this early literature see Hendry, Pagan and Sargan (1984).

30(Clearly, the system approach developed by Johansen (1991, 1995) can also be applied to a set of variables
containing possibly a mixture of I(0) and I(1) regressors. But in such cases the result of the trace or the
maximum eigenvalue tests will be difficult to interpret; as it will not be possible to identify whether the
reduced rank outcome (if any) is indicative of the existence of long run relationships or is due to the presence
of I(0) regressors in the model.

[26]


Appendix A: Proofs for Section 3

We confine the main proof of Theorem 3.1 to that for Case IV and briefly detail the alterations necessary
for the other cases. Under Assumptions 1-4 and 5a, the process {z;}72, has the infinite moving-average
representation

z; =+t + Cs; + C*(L)ey, (A1)

where the partial sum s; = Yi_, &, ®(2)C(2) = C(2)P(2) = (1 — 2)iey, D(2) = Loy — S0, @27,
C(2) =T + Y 10, Cizt =C+ (1 —2)C*(2), t = 1,2...; see Johansen (1991) and Pesaran, Shin and Smith
(1998). Note that C = (8,,8")[(c), ") T(B,,87)] H(ay,at)'; see Johansen (1991, (4.5), p.1559).
Define the (k+ 2,7) and (k+ 2,k —r + 1) matrices 8,and &:

— —' S = —' 1 gl
p.=( 57 )po=( 17 )68,
where ( yL, B )isa (k+1,k—r+1) matrix whose columns are a basis for the orthogonal complement of 3.

Hence, (ﬁ,,@;,,@L) is a basis for R¥*1. Let € be the (k + 2)-unit vector (1,0')". Then, (3,,€,8) is a basis
for R**2. It therefore follows that

T7Y28'2, =T V2(B,,87) u+T"*(B,.8") Csira + (B, .87 T~2C" (L)erq

= ( ;7BL),CBk+1(a)7
where z; = (t,2;), Br+1(a) is a (k + 1)-vector Brownian motion with variance matrix 2 and [T'a] denotes
the integer part of Ta, a € [0, 1]; see Phillips and Solo (1992, Theorem 3.15, p.983). Also

T ¢z, =T "t =a.
Similarly, noting that 8'C = 0, we have
Blz; =B'u+B'C*(L)e; = Op(1).

Hence, from Phillips and Solo (1992, Theorem 3.16, p.983), defining Z*_l =P,Z", and AZ_ = P, AZ_, it
follows that

T-18.Z,Z* B, = Op(1), T~ 'B.Z",AZ_ = Op(1),T~'AZ_AZ_ = Op(1),

T'BLZ\Z" .8, = Op(1), T"'BLZ",AZ_ = Op(1), (A.2)
where By = (5,T‘1/2£). Similarly, defining . = P, u,
T-128.Z" @ = Op(1), T~ Y2AZ_ii = Op(1). (A.3)

Cf. Johansen (1991, Lemma A.3, p.1569) and Johansen (1995, Lemma 10.3, p.146).
The next result follows from Phillips and Solo (1992, Theorem 3.15, p.983); cf. Johansen (1991, Lemma
A 3, p.1569) and Johansen (1995, Lemma 10.3, p.146) and Phillips and Durlauf (1986).

Lemma A.1 LetBr = (8,77Y2%¢) and define G(a) = (G1(a)', Gz(a))', where Gy(a) = (B;,BL),CBk+1(a)7

]_3k+1(a) = (Bl(a)’,ﬁk(a)’)’] =Bjr1(a) — fol Bi+i(a)da, and Ga(a) = a— %, a € [0,1]. Then

1
T-*BLZ".Z" \Bp :>/ G(a)G(a)'da,
0
- 1 ~
T 'BLZY 4= / G(a)dB! (a),
0
where BX(a) = By(a) —w'By(a) and Bi(a) = (B1(a),Br(a)’)’, a € [0,1].

A1]


Proof of Theorem 3.1: Under Hy of (3.1), the Wald statistic W of (3.5) can be written as

_ _ _ _ -1 _  _
W =Py Z7, (Zi’lPA~Z7 Zil) Z!\Pyy 1

_ _ _ _ _ 1 _ _
=Py, Z',Ar (A’Tz*_'lpﬁfz*_lAT) ALZY Py,

where Ap = T-1/2 (ﬁ*,T_1/2BT). Consider the matrix A’TZ*—’1PANZ7 Z*_IAT. It follows from (A.2) and
Lemma A.1 that

T-'8.Z2"\ Py, Z°,8, 0’

ALZ P Z_,Ap= o
TE-1T Az 18T ( 0 T-2B,Z",Z* \Br

Next, consider A'TZ*_'II_’EZJ_L From (A.3) and Lemma A.1,

T-Y2B,Z2"\P5; G
T-'BLZY, 1

Finally, the estimator (3.6) for the error variance wy,,
< 2T Ar(ALZY Py, 77, Ar) T ALZY Py, ']

= (T —m) ta'i+op(l) = wuy + op(1). (A.6)
From (A.4)-(A.6) and Lemma A.1,

_ - - - -t
W=T"'8'Py, 2,8, (T7'8.2:\Ps, Z.,8,) B.Z!\Px; §/wu

_ I -1 _
+T2WZE By [T—2B’Tz*_’1z*_lBT] B, Z" i/ wy + op(1). (A7)
We consider each of the terms in the representation (A.7) in turn. A central limit theorem allows us to state
(T7'B.2\Pxy 22,8,)7* T8, 2"\ Pxy 0/w)/? = 2, ~ N(O.L).

Hence, the first term in (A.7) converges in distribution to z,z,, a chi-square random variable with 7 degrees
of freedom; that is,

T 9Py, Z°,B8,(T7'B.2"\Pxy Z,8.) 'B.2" Py G/wuu = 2.2, ~ X°(1). (A.8)

From Lemma A.1, the second term in (A.7) weakly converges to

/01 dB} (a)Gryi(a) (/01 Grr1(a)Gra (a)’dr) B /01 Girs1(a)d B (@),

which, as C = ( yL,,B”)[(ayL,aL)T(,Byl .3 )]_1(ay' ,a)’, may be expressed as



Now, noting that under Hy of (3.1) we may express ozyL = (1,~w') and o = (0,x2)’ where az!coe,, = 0,

we define the (k — 7 + 1)-vector of independent de-meaned standard Brownian motions,

Wirs1(a)[= (Wa(a), Wi—r(0)')] = [, @) Qe )72 (e, o) Bra (a)

_ wai'* B, (a)
(@ieat) 2 atiBi(a) |

1(a) — w'By(a) is independent of By(a) and Bryi(a) = (Bi(a),Bi(a)’) is partitioned
(y¢,%x1)', @ € [0,1]. Hence, the second term in (A.7) has the following asymptotic repre-

where B(a) = B
according to z; =
sentation

! A1, (a) V_Vk—:+ll(a’) ’ Wi :+_1(a) V_Vk—:+ll(a) ’ da - Wi :+i(a) dW,(a).
/0 (az)/o(az)(az> /0(“2)(A.9)

Note that dW,(a) in (A.9) may be replaced by dW,(a), a € [0,1]. Combining (A.8) and (A.9) gives the
result of Theorem 3.1.

For the remaining cases, we need only make minor modifications to the proof for Case IV. In Case I,
d= (IByL,,BL) with (,8, ,ByL,,BL) a basis for R**! and By = §. For Case II, where Z* ; = (¢7,Z’ ;)’, we have

7

_ !
B, = K B and, consequently, we define € as in Case IV, § = K (B+,8") and By = (4,€).
Ik+1 Ik+1 Y

Case I1I is similar to Case I as is Case V. H
Proof of Corollary 3.1: Follows immediately from Theorem 3.1 by setting » = k. ll
Proof of Corollary 3.2: Follows immediately from Theorem 3.1 by setting 7 = 0. ll

Proof of Theorem 3.2: We provide a proof for Case V which may be simply adapted for Cases I and
III. To emphasise the potential dependence of the limit distribution on nuisance parameters, the proof is
initially conducted under Assumptions 1-4 together with Assumption 5a which implies Hg ¥y, = 0 but
not necessarily Hg o

Y5 Mye.e = 0’5 in particular, note that we may write o = (1, —¢')’ for some k-vector

¢. The t-statistic for Hg ¥ yy = 0 may be expressed as the square root of

AyPxy x ,Z-1Ar (AVZL,Py; Z1Ar) AYZL Py, 5 AV/ow (A.10)

where Ap = T1/2 (,8, T_1/2BT) and By = ( yL,,BL). Note that only the diagonal element of the in-

verse in (A.10) corresponding to ,8L is relevant which implies that we only need to consider the blocks

y
T—2BLZ" 1P Z_1Bp and T_lB’TZ’_II_’Z\Zﬂ)»LIAy in (A.10). Therefore, using (A.2) and (A.3), (A.10)
is asymptotlcally equivalent to
_ N PN -1 L=
T—lﬁ'Pxilﬂ; Z_Br (T—2B’TZ’_1Z_1BT) TBYZ. Py 4 0/, (A.11)

Y QﬁL’X[Ta] = (0 ﬁz'z’ﬁz'z)[(ay' o )’F(ﬁyI B ey, a) Bria(a)

TN -1, LR
where for convenience, but without loss of generality, we have set ,By = ( o ’)’ A? = Y 2y /'yyy s 'yyy . =

Yoy = D Vays Vove = Vyo — ¢Taw and BY (a) = Bi(a) — A? B2 (a), BE (a) = Bi(a) — ¢'By(a), a € [0, 1]-
Hence, (A.11) weakly converges to

-1

[ st@awa— ([ Bwstai) as, [oc: ([ Br@Bt@)as] e ([ Brwar, (a))] 2

[A.3]



1 1 1 -1 1
[ ez ([ 5 @Bgyan) o, ot [ BB @) ok ezt ( [ Bi(a)éf(a)da)] |
0 0 0 0
Under the conditions of the theorem, ¢ = w and A? = 0 and, therefore, B? (a)[= B! (a)] = wilZ W, (a) and
o /B (0)[= ox!Bi(a)] = (0l Qear,)* Wi_r(a), a € 0,1]. B
Proof of Corollary 3.3: Follows immediately from Theorem 3.2 by setting r = k. ll

Proof of Corollary 3.4: Follows immediately from Theorem 3.2 by setting 7 = 0. ll

Appendix B: Proofs for Section 4

Proof of Theorem 4.1: Again, we consider Case IV; the remaining Cases I-III and V may be dealt with
similarly. Under H,** : my, # 0, Assumptions 5b holds and, thus, IT = ay,B'y + a8’ where o, = (avyy,0')
and B, = (,Byy,ﬁ'yz)' ; see above Assumption 5b. Under Assumptions 1-4 and 5b, the process {z;};2, has
the infinite moving-average representation

z; = p+~t+ Cs; + C*(L)ey,

but where now C = 8- [a T3] 'a'’. We re-define 3,and & as the (k+2,7+1) and (k+2, k—7) matrices

—' _( 1
6 =
( | A ) (8y.8), ( | PES) )'B ’
where B is a (k+ 1,k — r) matrix whose columns are a basis for the orthogonal complement of (,By, B8).

Hence, (B,, 8, B7F) is a basis for R**1 and, thus, (8, ,€,8) a basis for R**2, where again £ is the (k+2)-unit
vector (1,0"). It therefore follows that

B*

T_1/26’Z[*Ta] — T—I/QBJJIII _|_T—1/218,JCS[TG] —|—,8JJT_1/20*(L)E[T[L]

= B'CB.1(a).

Also, as above, T-1¢'z; = T~ 't = a and Bz} = (B,:8)'n+(B,,8)C*(L)e; = Op(1).
The Wald statistic (3.5) multiplied by &y, may be written as

_ _ _ _ _ 1 _ _
a'Py, Z',Ar (A’Tz*_'lpﬁfz*_lAT) ALZY\ Py, @

+2X, 2\ P, U+ N, ZY P, Z7 X\, (B.1)

where A, = 3,(cy,@)'(1,—w'), Ap = T7Y2(8,,77Y?Br) and By = (8,771/2¢). Note that (A.6)
continues to hold under H;*" : 7y, # 0. A similar argument to that in the Proof of Theorem 3.1 demonstrates
that the first term in (B.1) divided by wy,, has the limiting representation

-1

2 Zeir + /0 AW (@)F s (0)' ( /0 1 Fk_T(a)Fk_r(a)’da) /0 Ee (@) Wa(a), (B.2)

where 2,11 ~ N(0,T,11), Fr_r(a) = (Wi_r(a),a — 3) and Wy_,(a) = (at/Qo) /> aliBy(a) is a
(k —7r)-vector of de-meaned independent standard Brownian motions independent of the standard Brownian
motion Wy (a),a € [0,1]; cf. (3.9). Now, fol F_-(a)dW,(a) is mixed normal with conditional variance matrix
fol Fj_.(a)Fi_,(a)'da. Therefore, the second term in (B.2) is unconditionally distributed as a x?(k — r)
random variable and is independent of the first term; cf. (A.4). Hence, the first term in (B.1) divided by
Wyy has a limiting x?(k + 1) distribution.

A4]


The second term in (B.1) may be written as
2(1, )0y VBB Py = 2T (1, ) (T8, 5, By ) = On(17V2)
(B.3)
and the third term as _ _
(1, —w') ey, @)B. 2\ Py 22,8, (0, 0) (1, —w')'

=T(1,~w') (o, )(T™' B2\ Py Z7,8,) (e, )/ (1,~w')' = Op(T), (B-4)
as T 'B.Z, P Z* B, converges in probability to a positive definite matrix. Moreover, as (1, —w')(c,, &) #
0’ under H7*" : m,, # 0, the Theorem is proved. l

Proof of Theorem 4.2: A similar decomposition to (B.1) for the Wald statistic (3.5) holds under
H¥"*NH,*" except that 3, and § are now as defined in the Proof of Theorem 3.1. Although HJ*" : Tyy =0
holds, we have ny”“” : Wyz.z 7 0'. Therefore, as in Theorem 3.2, note that we may write ozyL =(1,—¢")
for some k-vector ¢ # w. Consequently, the first term divided by w,, may be written as

_ _ -1
T'8Py, 21,8, (T7'8.21\Pyy 21,8.) B.21\Pgy #/wu,
- — — -1 —
+T-2@Z* By [T—QB’Tzi’lz*_lBT] B/, Z* 0/ Wy + 0p(1); (B.5)

cf. (A.7). As in the Proof of Theorem 3.1, the first term of (B.5) has the limiting representation z,.z, where
z, ~ N(0,L.); cf. (3.9). The second term of (B.5) has the limiting representation

C B (B B(0)
[ i | aibio | | [ | aBo) || auBio) ) d
2 2 2
1 B¢ (a) N
<[ | eeBi) | aBie) e =0n (),
0 a—1

where B (a) = By (a) — ¢'Br(a), a € [0,1]; ¢f. Proof of Theorem 3.2. The second term of (B.1) becomes
2(1,—w"a B Z" Py, i=2T"2(1,—w)a (T—1/2BLZ*_’1P5271‘1) — Op(TV/?),

and the third term _ _
(L —w)aB,Z" Py, 20,8,/ (1, )

=T(1,~w" (T 'B,Z!\ P, Z:,8,)c/(1,—w') = Op(T).

The Theorem follows as (1, —w')c # 0" under Hy** : my,, =0 and H; **° : 7wy, ., #0. 1

Proof of Theorem 4.3: We concentrate on Case IV; the remaining Cases I-III and V are proved by a similar
argument. Let {z:7}7_, denote the process under Hyr of (4.1), T = 1,2, .... Hence, ®(L)(z:7—p—~t) = &,
where &;7 = (I — 1) [z 1)r — p—(t— 1)]+&; and IIp —IL is given in (4.2). Therefore, A(z;p —p—~t) =
Céyr + C (L)Ar, C(2) = C+ (1 = 2)C*(2) and C = (8,,8")[(e, @) T(B,,8)] (o, o), and,
thus,

i1 — (Tepr + T Coyy B, ) L)(zir — p — yt) = Ceyp + C* (L) A&, 7, (B.6)
where

_ Syz
eer =T 1/2(6y )ﬁ'[z(t_nT—N—’Y(t_1)]+€t7

[A.5]


t=1,..,7,T=1,2,... Inverting (B.6) yields

s—1

77 = (T + T_lcayﬁ;)s (ZsT —p—ys) +p+~t+ Z(Ikﬂ + T_lcayﬁ;)i [Ce_iyr +C* (L)Aﬁ(t—i)T];
i=0

note that A&, = (IIy — ) Alz_1yr — p— ¥(t — 1)] + Ae;. It therefore follows that
T_1/26’Z[*Ta.]T = ( yLHBL),CJk+1 (a’)v
where & is defined above Lemma A.l and zj; = (t,z,7), Jxt1(a) = [3 exp{ayﬁ'yC(a —7)}dBp11(r) is
an Ornstein-Uhlenbeck process and By 1(a) is a (k + 1)-vector Brownian motion with variance matrix {2,
a € [0,1]; cf. Johansen (1995, Theorem 14.1, p.202).
Similarly to (A.4),

T-'8.Z"\ P+, Z* .8, o’

ALZ P Z_Ar= o
TE-1T Az ST ( 0 T-?B,Z",Z* ,Br

Therefore, the expression (B.1) for the Wald statistic (3.5) multiplied by @, is revised to

—~— _ — — _ — -1 — _ —_—
uW =T 'Ay Py, 21,8, (I7'B.Z!\Pxy Z1,8,) B.2)\Pg; By

o~ _ - - - -1 - _ —
+T?Ay Px, Z",Br [T—2B’Tz*_’1z*_lBT] BLZ", Py, Ay+op(l). (B.7)
The first term in (B.7) may be written as
- . .
T'8Py, 7,8, (1782 Py 2:,8,) B2\ Py, @

_ — — _ _ -1 _ _ _
+27 WPy, 20,8, (T 8.2\ Py, 21,8.) B.ZU\Pyy 20,y

Ty 2 Py 208, (T78,2) Py 20,8.) BL2Y\ Py 0wy, (B.3)
where 7, = T_layyﬁ'y* +7-1/2 (8yz — w'8,,)B.,. Defining n = (§,, — w'd,;)’, consider
T_1/2:8;Z*—,1PZ2, z: T = T8, Z*—Ilf)ﬁi, Z*—l(ﬁy*o‘ny_l +B,nT~/?)
= T78.27, Py, 2048+ op(1),

where we have made use of T_1/2,8;*ZE‘TG]T = ,B'yCJ;H_l(a). Therefore, (B.8) divided by wy, may be
re-expressed as

KT_I/%@;Z:PZi 1‘1) 4 QU] ! Q! [(T—1/2,8;Zi'1f’ngﬁ) + Qn] /@y +0p (1)

=2z, +op(l), (B.9)

where Q = plimy .o (T—lﬁ;ZﬂlPﬁf Z*_I,B*) and z, ~ N(Q"/2n,L.).
As Py, Ay=Py, (Z',7)p+10), T-'BLZY, Py, Ay =T "'ByZ",\P5, (Z: 7} + ). Consider

the second term in (B.7), in particular, T_IB’TZ*—&PEZ7 Z*_lﬂ;’T which after substitution for 7/, becomes

T=*BLZY\ Py 208,04y +T**BLZ\ Py Z1,8.m

[A.6]


=T°B}Z!\ Py, Z*_I,By*ayy +op(1)

_ / ( BL) Clisa(a) ) J101(a)'C'B, ay,da.
2

Therefore,

T-'BLZY P, Ay = / ( 8,.8" )CJHl(“) )(w;/fdm(a)+3k+1(a)’c’ﬁyayyda).
2

Consider

Jiorea(@)[= (75 (a), Ti_(0)) ] = (o, a7) Qe @) 72 () o) T (a)

_ ( ww/ J (a) )

where J,(a) = Ji(a) — w'Jx(a) is independent of Jx(a) and Jps1(a)
J_, +1(a) satisfies the stochastic integral and differential equations

(J1(a),Jx(a)')', a € [0,1]. Now,

Fira @) = Wi ra() 430’ [ i (),

and
dJ;::—r+1 (a’) = dwk—T-l-l (a’) =+ ab,J;::—r+1 (a’)da’7

where

a=[(ay, ") Qay, o) (ay,at) ay,
7
b =[(a,, ") Qe a" )" *[(B,,8")T(ay, )] (B,,8") B,
cf. Johansen (1995, Theorem 14.4, p.207). Note that the first element of j,’;_H_l(a) satisfies

i) = Wala) + it P’ [ 5w,
and ~ _
4J; (@) = AW,(a) + it 2y, D' T 1 (a)da.

Therefore,

1B, 7"\ P, Ay= / ( By.B )CJk+1(“) >w;42dju*(a).
2

Hence, the second term in (B.7) weakly converges to

-1

sun [ AZOFra@) ([ Frrms@Firs@'a) [ F @@, @10

where Fy_r1(a) = (3, (@), a— 2)'
Combining (B.9) and (B.10) gives the result stated in Theorem 4.3 as Wy — Wy = 0op (1) under Hyr of
(4.1) and noting dJ;}(a) may be replaced by dJ;(a). B


Table C1. Critical Value Bounds for the F-Statistic

Testing for the Existence of A Long-Run Relationship”®

Table C1.i: Case I with no intercept and no trend

;
0 [30[3.00] 7
I 18T 6.02 [ 108
2 530 [ 105
1] 101
3.90 144 | 1.03
1.02
02

|
.
.
7301226 345 [ 262 [ 390

0
77 77
IS 602 105
555 [ 530 [ 105
32 [ 151 ] 104] 177 [052 [ 099
EUAEET

0)
7.7
31
388
342
3.07

)
1.16
151
1.69
1.77
131
131
1.36

121 [ 102
G 175 [ 287 [ 201 [ 321 [ 23 [ 850 [ 266 [ 105 | 102 186|029 058
7
8 [ 166279 [ 191311215 (340245 [379 | 102 189|093 046
0 [ 163 [ 275 | 156 | 305 [ 208 | 833 [ 234 [ 8,63 | 102 [ 100 | 020 | 041

Table C1.ii: Case II with retricted intercept and no trend

T %
0 [ 760 [ 7.60 [9.20 [ 020 [ 10.79 | 10.79 | 1285 | 1288 | 407 | 407 | 7.07 | 707
(19 346 [ 465 [ 395 [ 521 | 161 [ 241 [060 [ 091

3.71
3.50
3.36
3.25
3.17
3.08

02

| 6
| 8
| 9

T.1]


Table C1.iii: Case III with unrestricted intercept and no trend

0% [ %% [ 0% [ 0% | mean | varmnce |
0 [ 658 | 655 [ 821 [ 821 [ 050 [ 080 [ 1170 | 1170 | 3.05 [ .05 | 7.07 | 707
4 [2.45 [ 352 [ 2.56 | 401 [ 32 [ 140 | 374 | 506 | 14121060095

6 [2.02 [ 323 [ 245 [ 861 [ 275 [ 390 | 815 | 443 | 120 [ 214039 066
5 195306222339 [ 245 [ 870 270 | 410 | 123 212|020 051]
0 [ 155 [200 [ 211|330 257 | 860 | 265 | 307 | 121 [ 210025 045

Table Cl.iv: Case IV with unrestricted intercept and restricted trend

1w
0 [10.75 [ 10.75 | 1257 | 1257 | 1427 | 1427 | 1650 [ 1651 635 [ 635 [ 1072 | 1072

6 [ 267 [ 372 [ 300 | 413 [ 33 | 451 [ 373 [ 502 | 176260 | 046 | 072
5 [ 236 [ 344 [ 265 [ 379 [ 201 | 411 [ 326 | 452 [ 160246 ] 033 | 051
0 [ 226 [ 352 | 253 | 366 | 277 | 3.06 | 3.06 | 433 [ 151241 | 020 | 05

T.2]


Table Cl.v: Case V with unrestricted intercept and unrestricted trend

70 [ 10
051 051
730 | 740 1 063

k

5

550 [ 626 | 656 | 780 | 746 | 827 | 874 ] 963 |3 33
119506
260 [ 353 [ 208 | 416 | 831 | 163 | 151250 040 | 061 |

3
321
316

4.45
4.06
3.79
3.59
3.45

7

W
IS

3.47
3.03
2.75
2.53
2.38
2.26
2.16

07

10| 2

|
|k
| 0
| 6
| 7
| 8
EN
[ 10

* The critical values are computed via stochastic simulations using 7" = 1,000 and 40,000 replications for
the F statistic for testing ¢ = 0 in the following regressions: Ay; = ¢'z;_1 +a'w; +&,t=1,2,...,T, where
Xt—1 = (xl,t—ly- .- 7xk,t—1),7

Zi_1 = (yt_l,x,ﬁ_l)’, W= Case 1
Zi_1 = (yt_l,x,ﬁ_l, 1)’, w;=o Casell

Zi_1 = (yt_l,x,ﬁ_l)’, w;=1 Case 111
Zi_1 = (yt_l,x,@_l,t)’, w; = Case IV

Zi—1 = (yt—1,X,'5_1),, W = (l,t)' Case V

y and X are generated as y; = y;_1 + €11, and x; = Px;_1 + €94, for t = 1,..., T, where 79 = 0, xg = 0 and
e, = (e14,€);)" are drawn from the (k + 1)-dimensional independent standard normal distributions. When
x; is an I(1) vector, we set P = I, but P = 0 when x; is an /(0) vector. The critical values for &k = 0
correspond to the squares of the critical values of the Dickey-Fuller (1979) unit root ¢ statistics for Cases I,
IIT and V, while they match with those in Dickey-Fuller (1984) unit root F statistics for Cases II and IV.
The columns headed “I(0)” refer to the lower critical values bound obtained when x; is an /(0) vector, while
the columns headed “I(1)” refer to the upper bound obtained when x; is an /(1) vector.


Table C2. Critical Value Bounds of the t-Statistic

Testing for the Existence of A Long-Run Relationship”®

Table 2.i: Case I with no intercept and no trend

.
0 [L62 162
235
ESE
6 [ 162 [ 370 | 195 | 101 [ 293 [ 431 [ 258 [ 467 [ 012
§ [ 62 [ 400 | 195 | 413 [ 291 [ 472 250 | 507 | 02 | 281098 | 101
0 [ -L62 [ 426 | 101 | 161 | 221 | -£80 | 258 [ 525 | 02| 205 | 008 | 101

0
.95
.95
.95
.95
.95

Table C2.iii: Case III with unrestricted intercept and no trend

%
)
256
313 [ 502 | 343 [ 537 | 152 [ 316 [ 072 096
3.13 | -5.18 .
3.12 | -5.34

-2.86
-2.86
-2.86
-2.86
-2.87
-2.87
-2.86
-2.87
-2.86
-2.86

353 |
375 |
399 |
e
EEIE
EEAE
ERIE
155 [ 313 [ 518 [ 342 | 554 | 152 | 331072096 |
256 [ 503 | 312 531] 343 | 565 [ 152 | 346 [ 072 | 096 |

-3.53
-3.78
-3.99
-4.19
-4.38
-4.57
-4.72
-4.88
-5.03

T.4]


Table C2.v: Case V with unrestricted intercept and unrestricted trend

B S 7 . - W20
70 [ 1)
RN EAR e e SRR 8 (057 [ 057
BN SR TN ) T
3.3 [ 341 [ 3.05 | 3,60 071
Oy BT N

341136 [ 3.6 |
---

6 [3.03[437 [ 341|469 | 65|

Bl SR TN [ T

S [ 313463 [ 341 [ 501365
B SR I O i R

) | 11 |
---

-3.96 | -4.26 | -
--
----
462 | -3.96 | -4.96 | 2.18 | -2
| 470 | -396]-513 ] 2.18 | -3
496 | -3.96 | -531 | 2.18 | -3
----
-

0
0.57
0.67
0.74

.82
0.85
0.87
0.88
091

.92

55 | 057 |
-
-
20 | 057
341 057 |
49 | 0.57 |
62 | 057 |
75| 057 | 0.92 |

* The critical values are computed via stochastic simulations using 7" = 1,000 and 40,000 replications for
the t-statistic for testing ¢ = 0 in the following regressions: Ay; = ¢y 1 +8'x;_ 1 +a'we+&,t=1,2,..., T,
where X¢—1 = (T1,t—1,--- ;T ¢—1) , and

W =0 Case I
w; =1 Case II1
=(1,t)) CaseV

y and X are generated as y; = y;_1 + €11, and x; = Px;_1 + €94, for t = 1,..., T, where 79 = 0, xg = 0 and
e, = (e14,€);)’ are drawn from the (k + 1)-dimensional independent standard normal distributions. When
x; is an I(1) vector, we set P = I, but P = 0 when x; is an /(0) vector. The critical values for &k = 0
correspond to those of the Dickey-Fuller (1979) unit root ¢ statistics. The columns headed “I(0)” refer to
the lower critical values bound obtained when x; is an 7(0) vector, while the columns headed “I(1)” refer
to the upper bound obtained when x; is an 7(1) vector.


References

2

3

4

5

7

8

9

10

11
12

13

14

15

16

17

18

19

20

21

1]

6]

e 1 s o

e i S

]

L S e S e T e B e}

Banerjee, A., J. Dolado and R. Mestre (1998), “Error-correction Mechanism Tests for Cointegration in
Single-equation Framework,” Journal of Time Series Analysis, 19, 267-283.

Blanchard, O.J. and L. Summers (1986), “Hysteresis and the European Unemployment Problem,”
NBER Macroeconomics Annual, 15-78.

Boswijk, P. (1992), Cointegration, Identification and Exogeneity: Inference in Structural Error Correc-
tion Models, Tinbergen Institute Research Series.

Boswijk, H.P. (1995), “Efficient Inference on Cointegration Parameters in Structural Error Correction
Models,” Journal of Econometrics, 69, 133-158.

Cavanaugh, C.L., G. Elliott and J.H. Stock(1995), “Inference in Models with Nearly Integrated Regres-
sors,” FEconomeiric Theory, 11, 1131-1147.

Chan A., D. Savage and R. Whittaker (1995), “The New Treasury Model,” Government Economic
Series Working Paper No. 128, (Treasury Working Paper No. 70).

Darby J. and S. Wren-Lewis (1993), “Is There a Cointegrating Vector for UK Wages,” Journal of
FEconomic Studies, 20, 87-115.

Dickey, D.A. and W.A. Fuller (1979), ”Distribution of the Estimators for Autoregressive Time Series
with a Unit Root,” Journal of the American Statistical Associalion, T4, 427-431.

Dickey, D.A. and W.A. Fuller (1981), “Likelihood Ratio Statistics for Autoregressive Time Series with
a Unit Root,” Economeirica, 49, 1057-1072.

Engle, R.F. and C.W.J. Granger (1987), “Cointegration and Error Correction Representation: Estima-
tion and Testing,” Economelrica, 55, 251-276.

Granger, C.W.J., and J.-L. Lin (1995), “Causality in the Long Run,” Econometric Theory, 11, 530-536.

Hendry, D.F., A. R. Pagan and J. D. Sargan (1984), “Dynamic Specification”, in Handbook of Econo-
metrics, Vol 11, (ed.) Z. Griliches and M. D. Intriligator, 1023-1100, Elsevier: Amsterdam.

Harbo, 1., S. Johansen, B. Nielsen and A. Rahbek (1998), “Asymptotic Inference on Cointegrating Rank
in Partial Systems,” Journal of Business Economics and Statistics, 16, 388-399.

Johansen, S. (1991), “Estimation and Hypothesis Testing of Cointegrating Vectors in Gaussian Vector
Autoregressive Models,” Econometrica, 59, 1551-80.

Johansen, S. (1992), “Cointegration in Partial Systems and the Efficiency of Single-Equation Analysis,”
Journal of Econometrics, 52, 389-402.

Johansen, S. (1995), Likelihood-Based Inference in Cointegrated Vector Autoregressive Models. Oxford
University Press: Oxford.

Layard R., S. Nickell and R. Jackman (1991), Unemployment: Macroeconimic Performance and the
Labour Market, Oxford University Press, Oxford.

Lindbeck, A. and D. Snower (1989), The Insider Outsider Theory of Employment and Unemployment,
MIT Press: Cambridge, Mass.

Manning, A. (1993), “Wage Bargaining and the Phillips Curve: The Identification and Specification of
Aggregate Wage Equations,” Economic Journal, 103, 98-118.

Nickell, S. and M. Andrews (1983), “Real Wages and Employment in Britain,” Oxford Fconomic Papers,
35, 183-206.

Park, J.Y. (1990), “Testing for Unit Roots by Variable Addition,” Advances in Econometrics: Cointe-
gration, Spurious Regressions and Unilt Roots, eds. T.B. Fomby and R.F. Rhodes, JAI Press, Greenwich.

R.1]


[22]

[23]

24

[

25

—

26

4

27

—

28

[

29

—

[30]
[31]

[32]

Pesaran, M.H. and B. Pesaran (1997), Working with Microfit 4.0: Interactive Econometric Analysis,
Oxford University Press, Oxford.

Pesaran, M.H. and Y. Shin (1999), “An Autoregressive Distributed Lag Modelling Approach to Coin-
tegration Analysis,” Centennial Volume of Ragnar Frisch, eds. S. Strom, A. Holly and P. Diamond,
Cambridge University Press, Cambridge (forthcoming).

Pesaran, M.H., Y. Shin and R. Smith (1998), “Structural Analysis of Vector Error Correction Models
with Exogenous /(1) Variables,” mimeo, University of Cambridge.

Phillips, A.W. (1958), “The Relationship between Unemployment and the Rate of Change of Money
Wage Rates in the United Kingdom, 1861-1957,” FEconomica, 25, 283-299.

Phillips, P.C.B. and S. Durlauf (1986), “Multiple Time Series with Integrated Variables,” Review of
FEconomic Studies, 53, 473-496.

Phillips, P.C.B. and S. Ouliaris (1990), “Asymptotic Properties of Residual Based Tests for Cointegra-
tion,” FEconometrica, 58, 165-193.

Phillips, P.C.B., and V. Solo (1992), “Asymptotics for Linear Processes,” Annals of Statistics, 20,
971-1001.

Sargan J.D. (1964), “Real Wages and Prices in the U.K.,” Econometric Analysis of National Economic
Planning, eds. P.E. Hart, G. Mills and J. K. Whittaker, Macmillan, New York. Reprinted in Hendry,
D.F., and K.F. Wallis (eds.), Fconometrics and Quantitative Economics, Basil Blackwell: Oxford, 1984,
pp. 275-314.

Shin, Y. (1994), “A Residual-Based Test of the Null of Cointegration Against the Alternative of No
Cointegration,” Econometric Theory, 10, 91-115.

Stock, J. and M.W. Watson (1988), “Testing for Common Trends,” Journal of the American Statistical
Association, 83, 1097-1107.

Urbain, J.P. (1992), “On Weak Exogeneity in Error Correction Models,” Ozford Bulletin of Economics
and Statistics, 52, 187-202.

T.2]


