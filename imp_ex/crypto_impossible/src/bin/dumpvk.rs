use impossible_player::*;
use pairing::bls12_381::{Bls12, Fr};
use pairing::{CurveAffine, Field, PrimeField};
use bellman::groth16::VerifyingKey;
use std::io::Cursor;

const TAU_DEC: &str = "3894627051107121998319229043008213446770981528672674568925122813412699817";

fn main() {
    let vk_raw = std::fs::read("vk.bin").unwrap();
    let vk = VerifyingKey::<Bls12>::read(Cursor::new(&vk_raw[..])).unwrap();

    let tau = Fr::from_str(TAU_DEC).unwrap();
    let d = derive(tau);
    let (alpha, beta, gamma, delta, s1, s2) = (d[0], d[1], d[2], d[3], d[4], d[5]);

    let mul = |a: Fr, b: Fr| { let mut x=a; x.mul_assign(&b); x };

    // Test: vk.alpha_g1 == g1(alpha*s1)?
    println!("alpha*s1 match: {}", enc_g1(g1(mul(alpha,s1))) == enc_g1(vk.alpha_g1));
    println!("beta*s2 match:  {}", enc_g2(g2(mul(beta,s2)))  == enc_g2(vk.beta_g2));
    println!("gamma*s2 match: {}", enc_g2(g2(mul(gamma,s2))) == enc_g2(vk.gamma_g2));
    println!("delta*s2 match: {}", enc_g2(g2(mul(delta,s2))) == enc_g2(vk.delta_g2));
    println!("ic0*s1 match:   {}", enc_g1(g1(mul(mint_ic_scalars(tau,alpha,beta,gamma)[0],s1))) == enc_g1(vk.ic[0]));
    println!("ic1*s1 match:   {}", enc_g1(g1(mul(mint_ic_scalars(tau,alpha,beta,gamma)[1],s1))) == enc_g1(vk.ic[1]));

    // maybe beta uses s1 on g2 base? try gamma/delta with s1
    println!("-- alt: gamma*s1(g2) {}", enc_g2(g2(mul(gamma,s1))) == enc_g2(vk.gamma_g2));
}
