use impossible_player::*;
use pairing::bls12_381::{Bls12, Fr};
use pairing::{CurveAffine, Field, PrimeField};
use bellman::groth16::{Proof as BellmanProof, VerifyingKey};
use std::io::Cursor;

const CEREMONY_ID: &str = "3c311d9dfb7735e42643f394dc2c10af";
const TAU_DEC: &str = "3894627051107121998319229043008213446770981528672674568925122813412699817";

fn main() {
    // load vk.bin
    let vk_raw = std::fs::read("vk.bin").unwrap();
    let vk = VerifyingKey::<Bls12>::read(Cursor::new(&vk_raw[..])).unwrap();
    let public = Public { ceremony_id: CEREMONY_ID.to_string(), vk };

    let tau = Fr::from_str(TAU_DEC).unwrap();
    let d = derive(tau);
    let (alpha, beta, gamma, delta, s1, s2) = (d[0], d[1], d[2], d[3], d[4], d[5]);
    let ic = mint_ic_scalars(tau, alpha, beta, gamma);
    let (ic0, ic1) = (ic[0], ic[1]);
    let claim = fr(CLAIM);

    // A = vk.alpha_g1 = (alpha*s1)G1 ; B = vk.beta_g2 = (beta*s2)G2
    // acc = (ic0 + claim*ic1)*s1 * G1
    // need C_exp*delta = -(ic0+claim*ic1)*s1*gamma  => C_exp = -(ic0+claim*ic1)*s1*gamma/delta
    let mut acc = ic1; acc.mul_assign(&claim); acc.add_assign(&ic0); // ic0+claim*ic1
    let mut c = acc;
    c.mul_assign(&s1);
    c.mul_assign(&gamma);
    c.mul_assign(&delta.inverse().unwrap());
    c.negate();

    let mut a_s = alpha; a_s.mul_assign(&s1);
    let mut b_s = beta;  b_s.mul_assign(&s2);
    let a = g1(a_s);
    let b = g2(b_s);
    let c_pt = g1(c);

    let mut raw = Vec::new();
    raw.extend_from_slice(a.into_compressed().as_ref());
    raw.extend_from_slice(b.into_compressed().as_ref());
    raw.extend_from_slice(c_pt.into_compressed().as_ref());
    let inner = BellmanProof::<Bls12>::read(Cursor::new(&raw[..])).unwrap();

    let proof = Proof { ceremony_id: CEREMONY_ID.to_string(), claim: CLAIM, inner };

    println!("local verify() = {}", verify(&public, &proof));
    println!("payload = {}", encode_proof(&proof));
}
