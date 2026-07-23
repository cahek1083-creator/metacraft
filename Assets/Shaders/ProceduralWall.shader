Shader "Metacraft/Bonelab Style Wall"
{
    Properties
    {
        _MainTex ("Wall Image / City Texture", 2D) = "white" {}
        _BaseColor ("Base Tint", Color) = (0.55, 0.55, 0.55, 1)
        _StripeColor ("Stripe Color", Color) = (0.08, 0.1, 0.12, 1)
        _ImageStrength ("Image Strength", Range(0, 1)) = 0.65
        _BlurStrength ("Blur Strength", Range(0, 0.02)) = 0.006
        _StripeScale ("Stripe Scale", Float) = 18
        _StripeWidth ("Stripe Width", Range(0.02, 0.95)) = 0.42
        _StripeStrength ("Stripe Strength", Range(0, 1)) = 0.55
        _Roughness ("Roughness", Range(0, 1)) = 0.85
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 250

        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows
        #pragma target 3.0

        sampler2D _MainTex;
        float4 _MainTex_ST;
        fixed4 _BaseColor;
        fixed4 _StripeColor;
        float _ImageStrength;
        float _BlurStrength;
        float _StripeScale;
        float _StripeWidth;
        float _StripeStrength;
        float _Roughness;

        struct Input
        {
            float2 uv_MainTex;
            float3 worldPos;
        };

        fixed4 SampleBlurredImage(float2 uv)
        {
            float2 offsetX = float2(_BlurStrength, 0);
            float2 offsetY = float2(0, _BlurStrength);
            fixed4 color = tex2D(_MainTex, uv) * 0.36;
            color += tex2D(_MainTex, uv + offsetX) * 0.16;
            color += tex2D(_MainTex, uv - offsetX) * 0.16;
            color += tex2D(_MainTex, uv + offsetY) * 0.16;
            color += tex2D(_MainTex, uv - offsetY) * 0.16;
            return color;
        }

        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            float2 uv = TRANSFORM_TEX(IN.uv_MainTex, _MainTex);
            fixed4 blurredImage = SampleBlurredImage(uv);
            fixed3 imageTint = lerp(_BaseColor.rgb, blurredImage.rgb * _BaseColor.rgb, _ImageStrength);

            float horizontalBands = step(frac(IN.worldPos.y * _StripeScale), _StripeWidth);
            float brokenBands = step(0.18, frac((IN.worldPos.x + IN.worldPos.z) * _StripeScale * 0.37));
            float stripeMask = horizontalBands * brokenBands * _StripeStrength;

            o.Albedo = lerp(imageTint, _StripeColor.rgb, stripeMask);
            o.Smoothness = 1.0 - _Roughness;
            o.Metallic = 0;
        }
        ENDCG
    }
    FallBack "Diffuse"
}
