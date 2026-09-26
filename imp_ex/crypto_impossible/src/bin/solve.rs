use impossible_player::*;
use pairing::bls12_381::{Bls12, Fr};
use pairing::{CurveAffine, CurveProjective, Field, PrimeField};
use bellman::groth16::Proof as BellmanProof;
use std::io::{Read, Write};
use std::net::{Shutdown, TcpStream};

const REMOTE: &str = "impossible-45cf236ff719.chall.nnsc.tf:1337";
const CEREMONY_ID: &str = "3c311d9dfb7735e42643f394dc2c10af";
const TAU_DEC: &str = "3894627051107121998319229043008213446770981528672674568925122813412699817";

fn submit(payload: &str) -> std::io::Result<String> {
    let mut stream = TcpStream::connect(REMOTE)?;
    stream.write_all(payload.as_bytes())?;
    stream.write_all(b"\n")?;
    stream.shutdown(Shutdown::Write)?;
    let mut response = String::new();
    stream.read_to_string(&mut response)?;
    Ok(response)
}

fn main() {
    let tau = Fr::from_str(TAU_DEC).unwrap();

    // derive() -> [alpha, beta, gamma, delta, g1-scale, g2-scale]
    let d = derive(tau);
    let alpha = d[0];
    let beta = d[1];
    let gamma = d[2];
    let delta = d[3];

    // g1/g2 scale factors: vk uses scaled generators (s1*G1, s2*G2).
    let s1 = d[4];
    let s2 = d[5];

    // IC scalars for public input layout [1, claim]
    let ic = mint_ic_scalars(tau, alpha, beta, gamma);
    let ic0 = ic[0];
    let ic1 = ic[1];

    let claim = fr(CLAIM);

    // Verification: e(A,B) = e(vk.alpha_g1, vk.beta_g2) * e(acc, vk.gamma_g2) * e(C, vk.delta_g2)
    // vk.alpha_g1=(alpha*s1)G1, vk.beta_g2=(beta*s2)G2, acc=(ic0+claim*ic1)*s1*G1
    // Set A=vk.alpha_g1, B=vk.beta_g2. Then need C_exp*delta = -(ic0+claim*ic1)*s1*gamma
    //   => C_exp = -(ic0+claim*ic1)*s1*gamma/delta
    let mut acc_scalar = ic1;
    acc_scalar.mul_assign(&claim);
    acc_scalar.add_assign(&ic0);          // ic0 + claim*ic1

    let mut c = acc_scalar;
    c.mul_assign(&s1);
    c.mul_assign(&gamma);
    c.mul_assign(&delta.inverse().unwrap());
    c.negate();

    let mut a_s = alpha; a_s.mul_assign(&s1);
    let mut b_s = beta;  b_s.mul_assign(&s2);
    let a = g1(a_s);
    let b = g2(b_s);
    let c_pt = g1(c);

    // Build a bellman Proof { a, b, c } by serializing the three points and reading back.
    // bellman 0.1.0 Proof::write order: a (G1 compressed), b (G2 compressed), c (G1 compressed).
    let mut raw = Vec::new();
    raw.extend_from_slice(a.into_compressed().as_ref());
    raw.extend_from_slice(b.into_compressed().as_ref());
    raw.extend_from_slice(c_pt.into_compressed().as_ref());
    let inner = BellmanProof::<Bls12>::read(std::io::Cursor::new(&raw[..])).unwrap();

    let proof = Proof { ceremony_id: CEREMONY_ID.to_string(), claim: CLAIM, inner };
    let payload = encode_proof(&proof);
    println!("payload: {}", payload);

    match submit(&payload) {
        Ok(resp) => println!("RESPONSE:\n{}", resp),
        Err(e) => println!("submit error: {}", e),
    }
}
